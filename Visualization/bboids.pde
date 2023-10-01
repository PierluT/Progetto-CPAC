import gifAnimation.*;
import processing.net.*;
import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress myRemoteLocation;

ArrayList<Boid> boids;
ArrayList<Avoid> avoids;

// Fall = background1, Spring = background2
PImage background1;
PImage background2;
// currently selected background
PImage currentbackground;

// Leaf = gif1, Butterfly = gif2
Gif gif1;
Gif gif2;
// currently selected boid animation
Gif currentGif;

// initialised signal at -1, this value will 
// be changed depending on the incoming OSC signal
int signal=-1;

float globalScale = .91;
String tool = "boids";

// boid control
float maxSpeed;
float friendRadius;
float crowdRadius;
float avoidRadius;
float coheseRadius;

// boids features switches
boolean option_friend = true;
boolean option_crowd = true;
boolean option_avoid = true;
boolean option_noise = true;
boolean option_cohese = true;
boolean option_changeColor = true;

// gui text messages
int messageTimer = 0;
String messageText = "";

void setup () {
  size(1024, 576);
  textSize(16);
  // initialise both backgrounds and animations
  background1 = loadImage("fall1.png");
  background2 = loadImage("spring1.png");
  currentbackground = background1;
  gif1 = new Gif(this, "leaf4.gif");
  gif2 = new Gif(this, "bf5.gif");
  //gif1.jump(int(random(50)));
  gif1.loop();
  gif2.loop();
  currentGif = gif1;
  currentGif.loop();
  recalculateConstants();
  boids = new ArrayList<Boid>();
  avoids = new ArrayList<Avoid>();
  
  // setting up a frame that can be avoided or not, depending on the scenario
  setupWalls();
  // setting up the IP address and the port to receive the OSC signals
  oscP5 = new OscP5(this, 12345);
  myRemoteLocation = new NetAddress("127.0.0.1", 12345);
}

// recalculate boids features
void recalculateConstants () {
  maxSpeed = 1.5 * globalScale;
  friendRadius = 60 * globalScale;
  crowdRadius = (friendRadius / 1.1); // era /1.3
  avoidRadius = 90 * globalScale;
  coheseRadius = friendRadius;
}

// obstacles
void setupWalls() {
  avoids = new ArrayList<Avoid>();
   for (int x = 0; x < width; x+= 20) {
    avoids.add(new Avoid(x, 10));
    avoids.add(new Avoid(x, height - 10));
  } 
}

void draw () {
  noStroke();
  colorMode(RGB);
  fill(0, 100);
  rect(0, 0, width, height);
  currentbackground.resize(width, height);
  background(currentbackground);
  if (signal == 1) { 
   // heart-shaped stick: fall and dissonance
   println("I received : " + signal); 
   boids.add(new Boid(random(width), random(height)));
   message(boids.size() + " Total Boid" + s(boids.size()));
   signal = -1;
   currentbackground = background1;
   currentGif = gif1;
   currentGif.loop();
   // setting up fall features
   option_friend = false;
   option_crowd = false;
   option_cohese = false;
   option_avoid = true;
   option_noise = true;
   option_changeColor = true;
} else if (signal == 0) {
   // sphere-shaped stick : spring and consonance
   println("I received : " + signal);
   boids.add(new Boid(random(width), random(height)));
   message(boids.size() + " Total Boid" + s(boids.size()));
   signal = -1;
   currentbackground = background2;
   currentGif = gif2;
   currentGif.loop();
   option_friend = true;
   option_crowd = true;
   option_cohese = true;
   option_avoid = false;
   option_noise = false;
   option_changeColor = false;
}
if (tool == "avoids") {
    noStroke();
    fill(0, 200, 200);
    ellipse(mouseX, mouseY, 15, 15);
  }
  for (int i = 0; i <boids.size(); i++) {
    Boid current = boids.get(i);
    current.go();
    current.draw();
  }

  for (int i = 0; i <avoids.size(); i++) {
    Avoid current = avoids.get(i);
    current.go();
    current.draw();
  }

  if (messageTimer > 0) {
    messageTimer -= 1; 
  }
  
  drawGUI();
}

void keyPressed () {
  if (key == 'q') {
    tool = "boids";
    message("Add boids");
  } /*else if (key == 'w') {
    tool = "avoids";
    message("Place obstacles");
  } */ else if (key == '1' || signal == 1) {
    // tested simulating the heart-shaped stick signal as key 1
     println("Ho ricevuto : " + signal);
     boids.add(new Boid(random(width), random(height)));
     message(boids.size() + " Total Boid" + s(boids.size()));
     currentbackground = background1;
     currentGif = gif1;
     currentGif.loop();
     option_friend = false;
     option_crowd = false;
     option_cohese = false;
     //option_avoid = false;
     option_noise = true;
     option_changeColor = true;
  } else if (key == '2' || signal == 0) { 
     // tested simulating the sphere-shaped stick signal as key 2
     println("Ho ricevuto : " + signal);
     boids.add(new Boid(random(width), random(height)));
     message(boids.size() + " Total Boid" + s(boids.size()));
     currentbackground = background2;
     currentGif = gif2;
     currentGif.loop();
     option_friend = true;
     option_crowd = true;
     option_cohese = true;
     //option_avoid = false;
     option_noise = false;
     option_changeColor = false;
  } else if (key == 'w') {
     setupWalls(); 
  }
  recalculateConstants();

}

int oscEvent(OscMessage theOscMessage){
  // receive OSC data
  if (theOscMessage.checkAddrPattern("/data")) {
    int value_received = theOscMessage.get(0).intValue();
    println("Value received: " + value_received);
    if(value_received == 0){
      signal = 0; // 0 = spring / consonance
    }
    else if (value_received == 1){
      signal = 1; // 0 = fall / dissonance
    }
  }
  return signal;
}

void drawGUI() {
   if(messageTimer > 0) {
     fill((min(30, messageTimer) / 30.0) * 255.0);
     text(messageText, 10, height - 20); 
   }
}

String s(int count) {
  return (count != 1) ? "s" : "";
}

String on(boolean in) {
  return in ? "on" : "off"; 
}

// tested simulating the hit of the stick with the mouse click
void mousePressed () {
  switch (tool) {
  case "boids":
    boids.add(new Boid(random(width), random(height)));
    message(boids.size() + " Total Boid" + s(boids.size()));
    break;
  }
}

void drawText (String s, float x, float y) {
  fill(0);
  text(s, x, y);
  fill(200);
  text(s, x-1, y-1);
}


void message (String in) {
   messageText = in;
   messageTimer = (int) frameRate * 3;
}
