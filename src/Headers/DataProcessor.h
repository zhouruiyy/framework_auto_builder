//
//  DataProcessor.h
//  MyFramework
//
//  Created by Framework Auto Builder
//  Copyright © 2024 Example Company. All rights reserved.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, DataFormat) {
    DataFormatJSON = 0,
    DataFormatXML,
    DataFormatPlist,
    DataFormatCSV
};

typedef NS_OPTIONS(NSUInteger, ProcessingOptions) {
    ProcessingOptionsNone = 0,
    ProcessingOptionsValidation = 1 << 0,
    ProcessingOptionsCompression = 1 << 1,
    ProcessingOptionsEncryption = 1 << 2,
    ProcessingOptionsLogging = 1 << 3
};

typedef void(^ProcessingCompletionBlock)(id _Nullable result, NSError * _Nullable error);

@interface DataProcessor : NSObject

@property (nonatomic, assign) DataFormat defaultFormat;
@property (nonatomic, assign) ProcessingOptions options;
@property (nonatomic, strong) NSString *encryptionKey;

+ (instancetype)sharedProcessor;

- (instancetype)initWithFormat:(DataFormat)format options:(ProcessingOptions)options;

// Data conversion methods
- (NSData * _Nullable)convertObject:(id)object toFormat:(DataFormat)format error:(NSError **)error;
- (id _Nullable)parseData:(NSData *)data fromFormat:(DataFormat)format error:(NSError **)error;

// Async processing methods
- (void)processData:(NSData *)data
         completion:(ProcessingCompletionBlock)completion;

- (void)processObject:(id)object
           withFormat:(DataFormat)format
           completion:(ProcessingCompletionBlock)completion;

// Validation methods
- (BOOL)validateData:(NSData *)data againstSchema:(NSDictionary *)schema error:(NSError **)error;
- (BOOL)validateObject:(id)object againstRules:(NSArray *)rules error:(NSError **)error;

// Utility methods
- (NSData * _Nullable)compressData:(NSData *)data;
- (NSData * _Nullable)decompressData:(NSData *)data;
- (NSData * _Nullable)encryptData:(NSData *)data withKey:(NSString *)key;
- (NSData * _Nullable)decryptData:(NSData *)data withKey:(NSString *)key;

@end

NS_ASSUME_NONNULL_END 