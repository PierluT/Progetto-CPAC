s.boot;
ServerOptions.outDevices;
s.options.outDevice_('Altoparlanti (Realtek(R) Audio)');

s.meter;
NetAddr("127.0.0.1", 57120);
// Configura il server OSC per accordi e melodia sulla stessa porta (57120)

// Synth for notes
(
SynthDef(\ring, {
  arg midinote = 62, amp = 2, dur = 3;
  var env, snd;
  snd = EnvGen.kr(Env.new([0,1,0],[0.01,dur,0.01]), doneAction: 2) * SinOsc.ar(midicps(midinote), 0, 0.2) ;
  // Aggiungi un filtro risonante
  snd = Resonz.ar(snd, midicps(midinote), 0.1);

  // Modula il volume
  snd = snd * amp;
  Out.ar([0, 1], snd);
 }).add;
)

// Synth for chords
(
SynthDef(\harpsi, { |outbus = 0, freq = 1000, amp = 0.1, gate = 1|
    var out;
    out = EnvGen.ar(Env.adsr, gate, doneAction: Done.freeSelf) * amp *
        SinOsc.ar(freq, 0.5, 0.75);
    Out.ar(outbus, out ! 2);
}).add;    // see below for more on .add
)

( // RECEIVER 1: PYTHON ONLY
OSCdef('OSCreceiver',
	{
		arg msg;
		var note,amp,dur;

		if (msg[1] =='nota'){
		msg.postln;
		note=msg[2];
		dur =msg[3];

			a = Synth(\ring,[\midinote, note, \dur, dur]);

		};
		if (msg[1] == 'quit'){
			msg.postln;
		   ~instr.set(\amp, 0);
		};


	},
	'/synth_control_melodia',);
)

//parte accordi
(
x = OSCFunc( { | msg, time, addr, port |
    var chord,note1,note2,note3,note4,pyFreq,pyAmp,pyDetune,pyLfo;

	// Handle end of sound
	if (msg[1] =='stop'){
		h.free;
	}
	{
	// handle class A message (freq and amplitude)
		if (msg[1]=='chord3'){
			// Parse message
			note1 = msg[2].asFloat;
			note2  = msg[3].asFloat;
			note3  = msg[4].asFloat;
			chord=[note1,note2, note3];
			msg.postln();
		};

			(
			p=Pbind(
				\instrument, \harpsi,
				\note, Pseq([chord],1),
				\dur, 1,
				\legato, 0.4,
				\amp, 0.1,
				//\strum, 0.1 // try 0, 0.1, 0.2, etc
			).play;
		)


	};

}, '/synth_control_accordi' );
)

s.quit;





