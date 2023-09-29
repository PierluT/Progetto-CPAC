s.boot;
s.meter;
NetAddr("127.0.0.1", 57120);
// Configura il server OSC per accordi e melodia sulla stessa porta (57120)

(
SynthDef(\ring, {
	arg midinote = 62, amp = 1.5, dur = 3;
	var env, snd;
	snd = EnvGen.kr(Env.new([0,1,0],[0.01,dur,0.01]), doneAction: 2) * SinOsc.ar(midicps(midinote), 0, 0.2) ;
	// Aggiungi un filtro risonante
	snd = Resonz.ar(snd, midicps(midinote), 0.1);

	// Modula il volume
	snd = snd * amp;
	Out.ar([0, 1], snd);
 }).add;
)

// melodia
(
SynthDef(\string_like_ring, {
	arg out=0, freq=440, pan=0, dur=0.5, amp=0.3;
	var env, snd, pluck;
	env = EnvGen.kr(Env.new([0, 1, 0], [0.01, dur, 0.01]), doneAction: 2);
	snd = SinOsc.ar(freq, 0, 0.2) * env;  // Utilizziamo SinOsc invece di PinkNoise

	// Aggiungi un filtro risonante
	snd = Resonz.ar(snd, freq, 0.1);

	pluck = PinkNoise.ar(Decay.kr(Impulse.kr(0.005), 0.05));
	env = freq.reciprocal;
	snd = CombL.ar(pluck, env, env, dur*6);

	// Modula il volume
	snd = snd * amp;
	snd = LeakDC.ar(LPF.ar(Pan2.ar(snd, pan), 12000)); // Applichiamo un filtro passa-basso e la gestione del DC offset

	DetectSilence.ar(snd, doneAction: 2);
	Out.ar([0, 1], snd);
}).add;
)


(
SynthDef(\string, {arg out=0, freq=440, pan=0, sustain=0.5, amp=0.3;
	var pluck, period, string;
	pluck = PinkNoise.ar(Decay.kr(Impulse.kr(0.005), 0.05));
	period = freq.reciprocal;
	string = CombL.ar(pluck, period, period, sustain*6);
	string = LeakDC.ar(LPF.ar(Pan2.ar(string, pan), 12000)) * amp;
	DetectSilence.ar(string, doneAction:2);
	Out.ar(out, string)
}).add;
)

(
SynthDef(\harpsi, { |outbus = 0, freq = 440, amp = 1, gate = 1|
    var out;
    out = EnvGen.ar(Env.adsr, gate, doneAction: Done.freeSelf) * amp *
        SinOsc.ar(freq, 0.5, 0.75);
    Out.ar(outbus, out ! 2);
}).add;    // see below for more on .add
)

(
SynthDef(\xilophone, {
	arg midinote = 62, amp = 1.5, dur = 1;
	var env, snd, freq;
	freq = midicps(midinote);

	// Crea un inviluppo con un attacco breve, una risonanza e un decadimento leggermente più lungo
	env = EnvGen.kr(Env.perc(0.01, 0.4), doneAction: 2);

	// Genera il suono con un impulso e modulazione di frequenza
	//snd = Impulse.ar(freq) * SinOsc.ar(freq * 2, 0, 0.2);

	snd = LPF.ar(SinOsc.ar(freq), 1000);

	// Applica l'inviluppo al suono
	snd = snd * env;

	// Modula il volume
	snd = snd * amp;

	Out.ar([0, 1], snd);
}).add;
)

// Synth for chords
(
SynthDef(\marimba, {arg out=0, amp=0.3, t_trig=1, sustain=0.5, gate=1,
	freq=220, rq=0.006;
	var env, signal;
	var rho, theta, b1, b2;
	env = EnvGen.kr(Env.adsr(0.0001, sustain, sustain, 2.5), gate,
		doneAction:2);
	b1 = 1.987 * 0.9889999999 * cos(0.09);
	b2 = 0.998057.neg;
	signal = SOS.ar(K2A.ar(t_trig), 0.3, 0.0, 0.0, b1, b2);
	signal = RHPF.ar(signal*0.8, freq, rq) + DelayC.ar(RHPF.ar(signal*0.9,
		freq*0.99999, rq*0.999), 0.02, 0.01223);
	signal = Decay2.ar(signal, 0.4, 0.3, signal);
	Out.ar(out, (signal*env)*(amp*0.65)!2);
}).add;
)

//Parte melodia
// SETTING the instrument as a global variable

(
~instr1=Synth(\marimba);
)

(
~instr1=Synth(\xilophone);
)

(
~instr1=Synth(\string);
)

(
~instr1=Synth(\string_like_ring);
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

			a = Synth(\ring,[\midinote, note, \dur, dur]); //xylophone

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
			chord.postln();
		};
		if (msg[1]=='chord4'){
			// Parse message
			note1 = msg[2].asFloat;
			note2  = msg[3].asFloat;
			note3  = msg[4].asFloat;
			note4  = msg[5].asFloat;
			chord=[note1,note2, note3,note4];
			chord.postln();
		};

			(
			p=Pbind(
				\instrument, \harpsi,
				\note, Pseq([chord],1),
				\dur, 1,
				\legato, 0.4,
				\amp, 0.2,
				//\strum, 0.1 // try 0, 0.1, 0.2, etc
			).play;
		)


	};

}, '/synth_control_accordi' );
)

s.quit;





