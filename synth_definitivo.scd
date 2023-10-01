s.boot;
s.meter;
NetAddr("127.0.0.1", 57120);
// Configura il server OSC per accordi e melodia sulla stessa porta (57120)

(
SynthDef(\flute, { arg scl = 0.2, freq = 440, ipress = 0.9, ibreath = 0.09, ifeedbk1 = 0.4, ifeedbk2 = 0.4, dur = 1, gate = 1, amp = 0.4;

	var kenv1, kenv2, kenvibr, kvibr, sr, cr, block;
	var poly, signalOut, ifqc;
	var aflow1, asum1, asum2, afqc, atemp1, ax, apoly, asum3, avalue, atemp2, aflute1;
	var fdbckArray;

	sr = SampleRate.ir;
	cr = ControlRate.ir;
	block = cr.reciprocal;

	ifqc = freq;

	// noise envelope
	kenv1 = EnvGen.kr(Env.new(
		[ 0.0, 1.1 * ipress, ipress, ipress, 0.0 ], [ 0.06, 0.2, dur - 0.46, 0.2 ], 'linear' )
	);
	// overall envelope
	kenv2 = EnvGen.kr(Env.new(
		[ 0.0, amp, amp, 0.0 ], [ 0.1, dur - 0.02, 0.1 ], 'linear' ), doneAction: 2
	);
	// vibrato envelope
	kenvibr = EnvGen.kr(Env.new( [ 0.0, 0.0, 1, 1, 0.0 ], [ 0.5, 0.5, dur - 1.5, 0.5 ], 'linear') );

	// create air flow and vibrato
	aflow1 = LFClipNoise.ar( sr, kenv1 );
	kvibr = SinOsc.ar( 5, 0, 0.1 * kenvibr );

	asum1 = ( ibreath * aflow1 ) + kenv1 + kvibr;
	afqc = ifqc.reciprocal - ( asum1/20000 ) - ( 9/sr ) + ( ifqc/12000000 ) - block;

	fdbckArray = LocalIn.ar( 1 );

	aflute1 = fdbckArray;
	asum2 = asum1 + ( aflute1 * ifeedbk1 );

	//ax = DelayL.ar( asum2, ifqc.reciprocal * 0.5, afqc * 0.5 );
	ax = DelayC.ar( asum2, ifqc.reciprocal - block * 0.5, afqc * 0.5 - ( asum1/ifqc/cr ) + 0.001 );

	apoly = ax - ( ax.cubed );
	asum3 = apoly + ( aflute1 * ifeedbk2 );
	avalue = LPF.ar( asum3, 2000 );

	aflute1 = DelayC.ar( avalue, ifqc.reciprocal - block, afqc );

	fdbckArray = [ aflute1 ];

	LocalOut.ar( fdbckArray );

	signalOut = avalue;

	OffsetOut.ar( 0, [ signalOut * kenv2, signalOut * kenv2 ] );
}).add;
)

(
~instr1=Synth(\flute);
)

// Synth for notes
(
SynthDef(\string_like_ring, {
	arg out=0, freq=440, pan=0, dur=0.5, amp=0.3;
	var env, snd, pluck;
	env = EnvGen.kr(Env.new([0, 1, 0], [0.01, dur, 0.01]), doneAction: 2);
	snd = SinOsc.ar(freq, 0, 0.2) * env;
	snd = Resonz.ar(snd, freq, 0.1);
	pluck = PinkNoise.ar(Decay.kr(Impulse.kr(0.005), 0.05));
	env = freq.reciprocal;
	snd = CombL.ar(pluck, env, env, dur*6);
	snd = snd * amp;
	snd = LeakDC.ar(LPF.ar(Pan2.ar(snd, pan), 12000));

	DetectSilence.ar(snd, doneAction: 2);
	Out.ar([0, 1], snd);
}).add;
)

// Synth for chords
(
SynthDef(\harpsi, { |outbus = 0, freq = 440, amp = 1, gate = 1|
    var out;
    out = EnvGen.ar(Env.adsr, gate, doneAction: Done.freeSelf) * amp *
        SinOsc.ar(freq, 0.5, 0.75);
    Out.ar(outbus, out ! 2);
}).add;    // see below for more on .add
)

(
~instr1=Synth(\harpsi);
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

			a = Synth(\string_like_ring,[\midinote, note, \dur, dur]);

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
				\dur, 1.5,
				\legato, 0.4,
				\amp, 0.4,
				//\strum, 0.1 // try 0, 0.1, 0.2, etc
			).play;
		)


	};

}, '/synth_control_accordi' );
)

s.quit;





