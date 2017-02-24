
//
//  ViewController.m
//  KDManager
//
//  Created by Zakai Hamilton on 10/7/15.
//  Copyright © 2015 Cisco. All rights reserved.
//

#import "ViewController.h"
#import "HttpServer.h"
#import "AppDelegate.h"
#include <ifaddrs.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <dlfcn.h>

//=======================================================
// Constants
//=======================================================
#define SBSERVPATH "/System/Library/PrivateFrameworks/SpringBoardServices.framework/SpringBoardServices"
#define IOS_CELLULAR    @"pdp_ip0"
#define IOS_WIFI        @"en0"
#define IOS_VPN         @"utun0"
#define IP_ADDR_IPv4    @"ipv4"
#define IP_ADDR_IPv6    @"ipv6"

//=======================================================
// Private interface
//=======================================================
@interface ViewController (Private)
@end

//=======================================================
// Public implementation
//=======================================================
@implementation ViewController {
    HTTPServer *httpServer;
    UISlider *slider;
    NSArray *numbers;
    int productType;
}

- (void) dealloc {
    httpServer = [HTTPServer sharedHTTPServer];
    [httpServer stop];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.deviceNameLabel.text = [[UIDevice currentDevice] name];
    [self.deviceNameLabel sizeToFit];
    
    //Set date
    NSDate *currentTime = [NSDate date];
    NSDateFormatter *dateFormatter = [[NSDateFormatter alloc] init];
    [dateFormatter setDateFormat:@"HH:mm"];
    self.timeLabel.text = [dateFormatter stringFromDate: currentTime];
    
    //print IP
    NSString* oldIP = [[NSUserDefaults standardUserDefaults] objectForKey:DEVICE_IP];
    self.ipLabel.text = oldIP;
    
    [self setSegments];
    
    [self updateIP];
}

-(void) updateIP
{
    NSString *ip = [HealthCheckNotification getIPAddress:YES];
    NSString* oldIP = [ [NSUserDefaults standardUserDefaults] objectForKey:DEVICE_IP];
    
    if (![ip isEqualToString:oldIP])
    {
        self.ipLabel.text = ip;
        self.ipLabel.textColor = [UIColor redColor];
    }
    
    [[NSUserDefaults standardUserDefaults] setObject:ip forKey:DEVICE_IP];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

-(void) setSegments
{
    NSNumber *savedProduct = [[NSUserDefaults standardUserDefaults] objectForKey:LAST_PRODUCTS];
    [self.productsSegments setSelectedSegmentIndex:[savedProduct integerValue]];
}

- (IBAction)launchApp:(id)sender {
    productType = (int)self.productsSegments.selectedSegmentIndex;
    [LaunchManager launchAppWithProduct:productType];
}
@end

// Used to disable warning for non-public methods
@interface UIApplication (Extensions)
- (BOOL)launchApplicationWithIdentifier:(id)identifier suspended:(BOOL)suspended;
@end


@implementation LaunchManager

+(BOOL) launchAppWithProduct:(ProductType)product
{
    NSURL *myURL;
    NSString * schemePath;
    
    switch (product) {
        case ProductKD: schemePath = @"productkd://launch"; break;
        case ProductHAPPY: schemePath = @"happy://launch"; break;
        case ProductZTV: schemePath = @"ztv://launch"; break;
        case ProductTME: schemePath = @"tme://launch"; break;
        case ProductYES: schemePath = @"yes://launch"; break;
        case ProductVTRON: schemePath = @"vtron://launch"; break;
        case ProductSOLARIS: schemePath = @"solaris://launch"; break;
        case ProductAPOLLO: schemePath = @"apollo://launch"; break;
        case ProductNET: schemePath = @"net://launch"; break;
        default:
            schemePath = @"productkd://launch"; break;
            break;
    }

    NSLog(@"Launching application with url: %@", schemePath);
    myURL = [NSURL URLWithString:schemePath];
    
    [[NSUserDefaults standardUserDefaults] setObject:[NSNumber numberWithInt:product] forKey:LAST_PRODUCTS];
    [[NSUserDefaults standardUserDefaults] synchronize];
    
    BOOL result = [[UIApplication sharedApplication] openURL:myURL];
    return result;
}

+ (void) launchApp:(NSString*)productString
{
    NSArray *products = @[@"KD", @"HAPPY", @"ZTV", @"TME", @"YES", @"VTRON", @"SOLARIS", @"APOLLO", @"NET"];
    NSUInteger indexOfTheObject = [products indexOfObject: productString];
    NSLog(@"name: %@ index: %ld", productString, (unsigned long) indexOfTheObject);
    
    ProductType productType = indexOfTheObject;
    BOOL result =  [LaunchManager launchAppWithProduct:productType];
    NSLog(@"Launch of application: %@", result ? @"Success" : @"Failed");
}

- (void) launchApp:(NSString*)productString
{
    [LaunchManager launchApp:productString];
}

-(NSString *)executeWithParams:(NSArray *)params
{
    NSString *productString = [NSString stringWithFormat:@"%@", params];
    [self performSelectorOnMainThread:@selector(launchApp:) withObject:productString waitUntilDone:false];
    return @"Success";
}

+ (NSString*) localIp
{
    return [HealthCheckNotification getIPAddress:YES];
}

@end


//=======================================================
// Private implementation
//=======================================================
@implementation ViewController (Private)
@end
