//
//  NetworkManager.h
//  MyFramework
//
//  Created by Framework Auto Builder
//  Copyright © 2024 Example Company. All rights reserved.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, NetworkStatus) {
    NetworkStatusUnknown = 0,
    NetworkStatusNotReachable,
    NetworkStatusReachableViaWiFi,
    NetworkStatusReachableViaWWAN
};

typedef void(^NetworkCompletionBlock)(NSData * _Nullable data, NSError * _Nullable error);
typedef void(^NetworkProgressBlock)(NSProgress *progress);

@protocol NetworkManagerDelegate <NSObject>

@optional
- (void)networkManager:(id)manager didChangeStatus:(NetworkStatus)status;
- (void)networkManager:(id)manager didReceiveData:(NSData *)data;

@end

@interface NetworkManager : NSObject

@property (nonatomic, weak) id<NetworkManagerDelegate> delegate;
@property (nonatomic, readonly) NetworkStatus currentStatus;
@property (nonatomic, strong) NSString *baseURL;
@property (nonatomic, assign) NSTimeInterval timeoutInterval;

+ (instancetype)sharedManager;

- (instancetype)initWithBaseURL:(NSString *)baseURL;

- (void)startMonitoring;
- (void)stopMonitoring;

- (NSURLSessionDataTask *)GET:(NSString *)path
                   parameters:(NSDictionary * _Nullable)parameters
                   completion:(NetworkCompletionBlock)completion;

- (NSURLSessionDataTask *)POST:(NSString *)path
                    parameters:(NSDictionary * _Nullable)parameters
                    completion:(NetworkCompletionBlock)completion;

- (NSURLSessionUploadTask *)uploadFile:(NSString *)filePath
                                toPath:(NSString *)path
                            parameters:(NSDictionary * _Nullable)parameters
                              progress:(NetworkProgressBlock _Nullable)progress
                            completion:(NetworkCompletionBlock)completion;

- (void)cancelAllRequests;

@end

NS_ASSUME_NONNULL_END 