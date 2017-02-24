//
//  KDManagerTests.m
//  KDManagerTests
//
//  Created by Zakai Hamilton on 16/06/2016.
//  Copyright © 2016 Cisco. All rights reserved.
//

#import <XCTest/XCTest.h>
#import "ViewController.h"

@interface KDManagerTests : XCTestCase

@end

@implementation KDManagerTests

- (void)setUp {
    [super setUp];
    // Put setup code here. This method is called before the invocation of each test method in the class.
}

- (void)tearDown {
    // Put teardown code here. This method is called after the invocation of each test method in the class.
    [super tearDown];
}



- (void)testLaunchApp {
    NSLog(@"Running test...");
#ifdef PRODUCT
    NSLog(@"Launch product %@", @PRODUCT);
    [LaunchManager launchApp:@PRODUCT];
#else
    NSLog(@"No Product specified");
#endif
#ifdef RETURN_IP
    NSString * localIp = [LaunchManager localIp];
    NSLog(@"Returning ip %@", localIp);
    XCTFail(@"ip=\"%@\"", localIp);
#endif
}

@end
