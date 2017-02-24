//
//  JSONRPCRequest.h
//  VE
//
//  Created by Gedalia Katz on 4/5/15.
//  Copyright (c) 2015 Tal Melamed. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface JSONRPCRequest : NSObject

@property (nonatomic, readonly) NSString *version;
@property (nonatomic, readonly) id objId;
@property (nonatomic, readonly) NSString *method;
@property (nonatomic, readonly) NSArray *params;

-(instancetype)initWithRequestBody:(NSData *)body;

@end
