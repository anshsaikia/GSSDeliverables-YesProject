//
//  JSONRPCRequest.m
//  VE
//
//  Created by Gedalia Katz on 4/5/15.
//  Copyright (c) 2015 Tal Melamed. All rights reserved.
//
#import <Foundation/NSJSONSerialization.h>
#import "JSONRPCRequest.h"
//#import "JSONUtils.h"

@implementation JSONRPCRequest

-(void)initWithData:(NSData *)data
{
    NSError *nserror = nil;
    NSDictionary *requestDict = [NSJSONSerialization JSONObjectWithData:data options:NSJSONReadingMutableContainers error:&nserror];
    NSLog(@"Milestones: request disctionary = [%@]", requestDict.debugDescription);
    _objId = [requestDict objectForKey:@"id"];
    _method = [requestDict objectForKey:@"method"];
    _params = [requestDict objectForKey:@"params"];
    _version = [requestDict objectForKey:@"jsonrpc"];
}

-(instancetype)initWithRequestBody:(NSData *)body
{
    self = [super init];
    
    if (self)
    {
        [self initWithData:body];
    }
    
    return self;
}

@end
