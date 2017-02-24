//
//  HealthCheckNotification.m
//  KDManager
//
//  Created by Boaz Warshawsky on 11/11/15.
//  Copyright © 2015 Cisco. All rights reserved.
//

#import "HealthCheckNotification.h"
#include <ifaddrs.h>
#include <arpa/inet.h>
#include <net/if.h>
#import "AppDelegate.h"

//=======================================================
// Constants
//=======================================================
#define IOS_CELLULAR    @"pdp_ip0"
#define IOS_WIFI        @"en0"
#define IOS_VPN         @"utun0"
#define IP_ADDR_IPv4    @"ipv4"
#define IP_ADDR_IPv6    @"ipv6"
#define VALUE 1


//=======================================================
// Private interface
//=======================================================
@interface HealthCheckNotification (Private)
- (void) readAppArguments;
- (void) doPost: (NSString*)url :(NSDictionary*)data;
@end


//=======================================================
// Public implementation
//=======================================================
@implementation HealthCheckNotification
- (id) init {
    self = [super init];
    if (self) {
        ecMachineIp_ = nil;
        [self readAppArguments];
    }
    return self;
}

- (BOOL) shouldPostHealthCheck {
    return ecMachineIp_ != nil;
}

- (NSString*) sendDeviceDetails {
    NSString *ip = [[self class] getIPAddress:YES];
    NSDictionary *dataDict = [[NSDictionary alloc] initWithObjectsAndKeys:
                              ip, @"device_ip",
                              nil];
    NSLog(@"sendDeviceDetails requested, target_url: %@, device_data: %@", ecMachineIp_, dataDict);
    [self doPost:ecMachineIp_ :dataDict];
    
    return ip;
}

+ (NSString *)getIPAddress:(BOOL)preferIPv4
{
    NSArray *searchArray = preferIPv4 ?
    @[ IOS_VPN @"/" IP_ADDR_IPv4, IOS_VPN @"/" IP_ADDR_IPv6, IOS_WIFI @"/" IP_ADDR_IPv4, IOS_WIFI @"/" IP_ADDR_IPv6, IOS_CELLULAR @"/" IP_ADDR_IPv4, IOS_CELLULAR @"/" IP_ADDR_IPv6 ] :
    @[ IOS_VPN @"/" IP_ADDR_IPv6, IOS_VPN @"/" IP_ADDR_IPv4, IOS_WIFI @"/" IP_ADDR_IPv6, IOS_WIFI @"/" IP_ADDR_IPv4, IOS_CELLULAR @"/" IP_ADDR_IPv6, IOS_CELLULAR @"/" IP_ADDR_IPv4 ] ;
    
    NSDictionary *addresses = [self getIPAddresses];
    NSLog(@"addresses: %@", addresses);
    
    __block NSString *address = NULL;
    [searchArray enumerateObjectsUsingBlock:^(NSString *key, NSUInteger idx, BOOL *stop)
     {
         address = addresses[key];
         if(address && [self validateIp:address]) {
             *stop = YES;
         }
     } ];
    NSString * finalAddress = address ? address : @"0.0.0.0";
    NSLog(@"Found ip: %@", finalAddress);
    return finalAddress;
}

+ (BOOL) validateIp: (NSString *) candidate {
    NSString *urlRegEx =
    @"((\\w)*|([0-9]*)|([-|_])*)+([\\.|/]((\\w)*|([0-9]*)|([-|_])*))+";
    NSPredicate *urlTest = [NSPredicate predicateWithFormat:@"SELF MATCHES %@", urlRegEx];
    return [urlTest evaluateWithObject:candidate];
}

+ (NSDictionary *)getIPAddresses
{
    NSMutableDictionary *addresses = [NSMutableDictionary dictionaryWithCapacity:8];
    
    // retrieve the current interfaces - returns 0 on success
    struct ifaddrs *interfaces;
    if(!getifaddrs(&interfaces)) {
        // Loop through linked list of interfaces
        struct ifaddrs *interface;
        for(interface=interfaces; interface; interface=interface->ifa_next) {
            if(!(interface->ifa_flags & IFF_UP) /* || (interface->ifa_flags & IFF_LOOPBACK) */ ) {
                continue; // deeply nested code harder to read
            }
            const struct sockaddr_in *addr = (const struct sockaddr_in*)interface->ifa_addr;
            int bufSize = MAX(INET_ADDRSTRLEN, INET6_ADDRSTRLEN);
            char addrBuf[ bufSize ];
            memset(addrBuf, 0, bufSize);
            if(addr && (addr->sin_family==AF_INET || addr->sin_family==AF_INET6)) {
                NSString *name = [NSString stringWithUTF8String:interface->ifa_name];
                NSString *type = NULL;
                if(addr->sin_family == AF_INET) {
                    if(inet_ntop(AF_INET, &addr->sin_addr, addrBuf, INET_ADDRSTRLEN)) {
                        type = IP_ADDR_IPv4;
                    }
                } else {
                    const struct sockaddr_in6 *addr6 = (const struct sockaddr_in6*)interface->ifa_addr;
                    if(inet_ntop(AF_INET6, &addr6->sin6_addr, addrBuf, INET6_ADDRSTRLEN)) {
                        type = IP_ADDR_IPv6;
                    }
                }
                if(type) {
                    NSString *key = [NSString stringWithFormat:@"%@/%@", name, type];
                    addresses[key] = [NSString stringWithUTF8String:addrBuf];
                }
            }
        }
        // Free memory
        freeifaddrs(interfaces);
    }
    return [addresses count] ? addresses : nil;
}

@end


//=======================================================
// Private implementation
//=======================================================
@implementation HealthCheckNotification (Private)
- (void) readAppArguments {
#ifdef EC_MACHINE_IP
    ecMachineIp_ = @EC_MACHINE_IP;
#else
    NSArray *arguments = [[NSProcessInfo processInfo] arguments];
    
    for (int i = 0 ; i < [arguments count]; i++) {
        NSString *argument = [arguments objectAtIndex:i];
        if ([argument containsString:@"ec_machine_ip="]) {
            NSArray* splitArgument = [argument componentsSeparatedByString:@"="];
            ecMachineIp_ = [splitArgument objectAtIndex:VALUE];
        }
    }
#endif
    NSLog(@"EC MACHINE IP='%@'", ecMachineIp_);
}

- (void) doPost: (NSString*)url :(NSDictionary*)data {
    NSError *error;
    NSData *postData = [NSJSONSerialization dataWithJSONObject:data options:0 error:&error];
    NSString *postLength = [NSString stringWithFormat:@"%lu",(unsigned long)[postData length]];
    NSMutableURLRequest *request = [[NSMutableURLRequest alloc] init];
    [request setURL:[NSURL URLWithString:url]];
    [request setHTTPMethod:@"POST"];
    [request setValue:postLength forHTTPHeaderField:@"Content-Length"];
    [request setValue:@"application/x-www-form-urlencoded" forHTTPHeaderField:@"Content-Type"];
    [request setHTTPBody:postData];
    NSError *err = nil;
    NSURLResponse *response = nil;
    [NSURLConnection sendSynchronousRequest:request returningResponse:&response error:&err];
    
    NSLog(@"\n\nresponse: %@ error:%@\n\n",response, err);
    
    if (err) {
        [[NSUserDefaults standardUserDefaults] setBool:NO forKey:LAST_HEALTH_OK];
        _status = [NSString stringWithFormat:@"url: '%@' error: '%@'", url, [err localizedDescription]];
    }
    else {
        [[NSUserDefaults standardUserDefaults] setBool:YES forKey:LAST_HEALTH_OK];
        _status = @"Health Check Successful";
    }
    [[NSUserDefaults standardUserDefaults] synchronize];
}

@end
