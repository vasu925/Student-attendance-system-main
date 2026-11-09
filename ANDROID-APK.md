# AttendEase Android APK

This Android wrapper opens the existing production AttendEase site in a native Android WebView. It does not copy the Flask backend or database into the APK. Sign-in, attendance, and data remain on the existing HTTPS service.

## Build
1. Open the repository's GitHub Actions tab.
2. Select **Build AttendEase Android APK** and choose **Run workflow**.
3. Wait for the workflow to finish successfully.
4. Open the completed run and download the **AttendEase-Android-APK** artifact.
5. Extract the ZIP and install `app-debug.apk` on an Android device. Allow installation from that source when Android asks.

This debug APK is for testing and direct sharing. A Play Store release needs a separately signed release build and a private signing key.
