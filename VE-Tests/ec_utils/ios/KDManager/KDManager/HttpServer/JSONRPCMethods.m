//
//  JSONRPCMethods.m
//  VE
//
//  Created by Gedalia Katz on 4/7/15.
//  Copyright (c) 2015 Tal Melamed. All rights reserved.
//

#import "JSONRPCMethods.h"

@implementation JSONRPCMethods

NSMutableDictionary *requestHandlers = nil;

-(void)registerMethod:(NSString *)method RequestHandler:(id<IJSONRPCMethodHandler>)handler
{
    if (requestHandlers)
    {
        requestHandlers[method] = handler;
    }
}

-(BOOL)methodSupported:(NSString *)method
{
    if (requestHandlers[method] != nil)
    {
        return  YES;
    }
    
    return NO;
}

-(NSString *)executeMethod:(NSString *)method WithParams:(NSArray *)params
{
    id<IJSONRPCMethodHandler> methodHandler = requestHandlers[method];
    NSString *responseString = nil;
    
    if (methodHandler)
    {
        responseString = [methodHandler executeWithParams:params];
    }
    
    return responseString;
}

+ (JSONRPCMethods *)sharedJSONRPCMethods
{
    static JSONRPCMethods *sharedJSONRPCMethods = nil;
    
    if (sharedJSONRPCMethods == nil)
    {
        sharedJSONRPCMethods = [[JSONRPCMethods alloc] init];
        
        if (sharedJSONRPCMethods)
        {
            requestHandlers = [[NSMutableDictionary alloc] init];
        }
    }
    
    return sharedJSONRPCMethods;
}

@end
