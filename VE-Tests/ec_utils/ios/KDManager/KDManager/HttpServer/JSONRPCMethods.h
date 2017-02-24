//
//  JSONRPCMethods.h
//  VE
//
//  Created by Gedalia Katz on 4/7/15.
//  Copyright (c) 2015 Tal Melamed. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol IJSONRPCMethodHandler <NSObject>

-(NSString *)executeWithParams:(NSArray *)params;

@end

@interface JSONRPCMethods : NSObject

-(void)registerMethod:(NSString *)method RequestHandler:(id<IJSONRPCMethodHandler>)handler;
-(BOOL)methodSupported:(NSString *)method;
-(NSString *)executeMethod:(NSString *)method  WithParams:(NSArray *)params;
+ (JSONRPCMethods *)sharedJSONRPCMethods;

@end
