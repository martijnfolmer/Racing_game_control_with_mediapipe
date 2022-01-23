# Controlling a game using mediapipe hand tracking
These scripts use the Google mediapipe hand tracking solution in combination with a webcam in order to send game instructions to a racing game. It features 2 control schemes, one with a steering wheel which controls both acceleration/decceleration and steering, and an alternate one that decouples both and assigns a functionality to each hand. The alternate control scheme allows for better control, because you don't have to worry about keeping your hands the same distance.

In order to run this, either start up the 'Virtual_steering_mediapipe' for the steering wheel option, or 'virtual_steering_mediapipe_alternate_control_scheme' for the alternate version. The inputs are send to the game using GamePad, so as long as the game you have open is compatible with xbox 360 controllers, it should work.

For an added bonus content, try using this to control a first person shooter, you will quickly go mad.

CONTROL SCHEME 1 : steering wheel
![control_scheme_1](https://user-images.githubusercontent.com/31698991/150687168-0495297a-5f90-437f-8157-121ffab89db1.jpg)


CONTROL SCHEME 2 : alternate
![control_scheme_2](https://user-images.githubusercontent.com/31698991/150687167-fefcbb16-23f7-4046-8fab-bbb3688c0aa2.jpg)

Good luck and happy coding.
