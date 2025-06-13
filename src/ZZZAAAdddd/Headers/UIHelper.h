//
//  UIHelper.h
//  MyFramework
//
//  Created by Framework Auto Builder
//  Copyright © 2024 Example Company. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, AnimationType) {
    AnimationTypeFade = 0,
    AnimationTypeSlide,
    AnimationTypeScale,
    AnimationTypeBounce
};

typedef NS_ENUM(NSInteger, AlertStyle) {
    AlertStyleDefault = 0,
    AlertStyleSuccess,
    AlertStyleWarning,
    AlertStyleError
};

@interface UIHelper : NSObject

// Color utilities
+ (UIColor *)colorFromHexString:(NSString *)hexString;
+ (UIColor *)colorFromHexString:(NSString *)hexString alpha:(CGFloat)alpha;
+ (NSString *)hexStringFromColor:(UIColor *)color;

// Image utilities
+ (UIImage * _Nullable)imageWithColor:(UIColor *)color size:(CGSize)size;
+ (UIImage * _Nullable)resizeImage:(UIImage *)image toSize:(CGSize)size;
+ (UIImage * _Nullable)cropImage:(UIImage *)image toRect:(CGRect)rect;
+ (UIImage * _Nullable)roundedImage:(UIImage *)image cornerRadius:(CGFloat)radius;

// View utilities
+ (void)addShadowToView:(UIView *)view
                 offset:(CGSize)offset
                 radius:(CGFloat)radius
                opacity:(CGFloat)opacity
                  color:(UIColor *)color;

+ (void)addBorderToView:(UIView *)view
                  width:(CGFloat)width
                  color:(UIColor *)color
           cornerRadius:(CGFloat)cornerRadius;

+ (void)addGradientToView:(UIView *)view
               startColor:(UIColor *)startColor
                 endColor:(UIColor *)endColor
                direction:(NSInteger)direction;

// Animation utilities
+ (void)animateView:(UIView *)view
               type:(AnimationType)type
           duration:(NSTimeInterval)duration
         completion:(void (^ _Nullable)(BOOL finished))completion;

+ (void)fadeInView:(UIView *)view duration:(NSTimeInterval)duration;
+ (void)fadeOutView:(UIView *)view duration:(NSTimeInterval)duration;

// Alert utilities
+ (void)showAlertInViewController:(UIViewController *)viewController
                            title:(NSString *)title
                          message:(NSString *)message
                            style:(AlertStyle)style
                       completion:(void (^ _Nullable)(void))completion;

+ (void)showActionSheetInViewController:(UIViewController *)viewController
                                  title:(NSString * _Nullable)title
                                message:(NSString * _Nullable)message
                                actions:(NSArray<UIAlertAction *> *)actions;

// Layout utilities
+ (void)centerView:(UIView *)view inSuperview:(UIView *)superview;
+ (void)constrainView:(UIView *)view toSuperview:(UIView *)superview withInsets:(UIEdgeInsets)insets;

// Device utilities
+ (BOOL)isIPad;
+ (BOOL)isIPhone;
+ (CGFloat)screenWidth;
+ (CGFloat)screenHeight;
+ (CGFloat)statusBarHeight;
+ (CGFloat)navigationBarHeight;

@end

NS_ASSUME_NONNULL_END 