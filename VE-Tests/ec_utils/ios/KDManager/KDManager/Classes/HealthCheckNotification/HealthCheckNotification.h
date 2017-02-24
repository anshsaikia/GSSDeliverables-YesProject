//
//  HealthCheckNotification.h
//  KDManager
//
//  Created by Boaz Warshawsky on 11/11/15.
//  Copyright © 2015 Cisco. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface HealthCheckNotification : NSObject
{
    @private
    NSString *ecMachineIp_;
}
- (NSString*) sendDeviceDetails;
- (BOOL) shouldPostHealthCheck;
+ (NSString *)getIPAddress:(BOOL)preferIPv4;
@property(assign) NSString * status;

@end
