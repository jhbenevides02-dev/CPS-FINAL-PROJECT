/**
* REALLY simple processing sketch for using webcam input
* This sends 300 input values (20x15 grid of brightness, 0-1) to port 6448 using message /wek/inputs
* Set the number of inputs in Wekinator to 300 (= numHoriz * numVert)
**/

import processing.video.*;
import oscP5.*;
import netP5.*;

int numPixelsOrig;
int numPixels;
boolean first = true;
boolean useDefaultCamera = true; // true: let Processing pick the camera; false: use cameraIndex below
int cameraIndex = 0; // which entry of the "Available cameras" list to use; try 1 if 0 stays black
String centerPixelHex = ""; // debug: ARGB of the centre pixel of the last camera frame
int framesReceived = 0; // debug: camera frames received so far

int boxWidth = 32;
int boxHeight = 32;

int numHoriz = 640/boxWidth;
int numVert = 480/boxHeight;

float[] downPix = new float[numHoriz * numVert]; // brightness per block, 0-1


Capture video;

OscP5 oscP5;
NetAddress dest;

void setup() {
 // colorMode(HSB);
  size(640, 480); // default renderer; P2D can return empty video.pixels

  String[] cameras = Capture.list();

  if (cameras == null) {
    println("Failed to retrieve the list of available cameras, will try the default...");
    video = new Capture(this, 640, 480);
    video.start();
  } else if (cameras.length == 0) {
    println("There are no cameras available for capture.");
    exit();
  } else {
    println("Available cameras:");
    for (int i = 0; i < cameras.length; i++) {
      println(i + ": " + cameras[i]);
    }

   if (useDefaultCamera) {
      video = new Capture(this, 640, 480);
    } else {
      video = new Capture(this, 640, 480, cameras[cameraIndex]);
    }

    // Start capturing the images from the camera
    video.start();
    
    numPixelsOrig = video.width * video.height;
    loadPixels();
    noStroke();
  }
  
  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this,9000);
  dest = new NetAddress("127.0.0.1",6448);
  
}

void draw() {
  
  if (video.available() == true) {
    video.read();
    framesReceived++;
    centerPixelHex = hex(video.get(video.width / 2, video.height / 2)) + "  size " + video.width + "x" + video.height;

    video.loadPixels(); // Make the pixels of video available
    /*for (int i = 0; i < numPixels; i++) {
      int x = i % video.width;
      int y = i / video.width;
      float xscl = (float) width / (float) video.width;
      float yscl = (float) height / (float) video.height;
      
      float gradient = diff(i, -1) + diff(i, +1) + diff(i, -video.width) + diff(i, video.width);
      fill(color(gradient, gradient, gradient));
      rect(x * xscl, y * yscl, xscl, yscl);
    } */
  int boxNum = 0;
  int tot = boxWidth*boxHeight;
  for (int x = 0; x < 640; x += boxWidth) {
     for (int y = 0; y < 480; y += boxHeight) {
        float sum = 0;

        for (int i = 0; i < boxWidth; i++) {
           for (int j = 0; j < boxHeight; j++) {
              int index = (x + i) + (y + j) * 640;
              sum += brightness(video.pixels[index]);
           }
        }
       downPix[boxNum] = sum / tot / 255.0; // average brightness scaled to 0-1
       boxNum++;
      /* if (first) {
         println(boxNum);
       } */
     }
  }
  if(frameCount % 2 == 0)
    sendOsc(downPix);

  }
  first = false;

  // Full-window preview of the averaged blocks (exactly what is sent to Wekinator).
  // Drawn every frame, not only when a new camera frame arrives, so the P2D buffer never stays empty.
  background(0);
  int p = 0;
  for (int x = 0; x < 640; x += boxWidth) {
    for (int y = 0; y < 480; y += boxHeight) {
      fill(downPix[p] * 255);
      rect(x, y, boxWidth, boxHeight);
      p++;
    }
  }

  fill(255, 0, 0);
  text("Camera frames received: " + framesReceived + "  block0 = " + nf(downPix[0], 1, 3), 10, 30);
  text("Centre pixel (ARGB): " + centerPixelHex, 10, 50);
  text("Sending " + downPix.length + " inputs to port 6448 using message /wek/inputs", 10, 10);

}

float diff(int p, int off) {
  if(p + off < 0 || p + off >= numPixels)
    return 0;
  return red(video.pixels[p+off]) - red(video.pixels[p]) +
         green(video.pixels[p+off]) - green(video.pixels[p]) +
         blue(video.pixels[p+off]) - blue(video.pixels[p]);
}

void sendOsc(float[] px) {
  OscMessage msg = new OscMessage("/wek/inputs");
   for (int i = 0; i < px.length; i++) {
      msg.add(px[i]);
   }
  oscP5.send(msg, dest);
}