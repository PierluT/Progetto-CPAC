class Avoid {
   PVector pos;
   
   Avoid (float xx, float yy) {
     pos = new PVector(xx,yy);
   }
   
   void go () {
     
   }
   
   void draw () {
     noStroke();
     fill(255, 255, 255);
     ellipse(pos.x, pos.y, 15, 15);
   }
}
