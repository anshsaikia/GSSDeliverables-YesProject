//
//  ViewController.h
//  KDManager
//
//  Created by Zakai Hamilton on 10/7/15.
//  Copyright © 2015 Cisco. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "HealthCheckNotification.h"
#import "JSONRPCMethods.h"

typedef NS_ENUM(NSInteger, ProductType) {
    ProductKD,
    ProductHAPPY,
    ProductZTV,
    ProductTME,
    ProductYES,
    ProductVTRON,
    ProductSOLARIS,
    ProductAPOLLO,
    ProductNET,
};

@interface ViewController : UIViewController
{
    @private
    HealthCheckNotification *healthCheckNotifier_;
    
}
@property (weak, nonatomic) IBOutlet UIView *launchButton;
@property (weak, nonatomic) IBOutlet UIView *containerView;
@property (weak, nonatomic) IBOutlet UILabel *deviceNameLabel;
@property (weak, nonatomic) IBOutlet UISegmentedControl *productsSegments;
@property (weak, nonatomic) IBOutlet UILabel *timeLabel;
@property (weak, nonatomic) IBOutlet UILabel *ipLabel;
@property (weak, nonatomic) IBOutlet UILabel *statusLabel;

- (IBAction)launchApp:(id)sender;

@end

@interface LaunchManager : NSObject<IJSONRPCMethodHandler>
+(BOOL) launchAppWithProduct:(ProductType)product;
+(void) launchApp:(NSString*)productString;
+(NSString*) localIp;
@end
