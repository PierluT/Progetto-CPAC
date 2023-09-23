// definition of the instrument
(
SynthDef("moog", {
	arg vibr=0, cutoff=0.5, midinote=60, amp=0;
	var osc1, osc2, osc3, f0, vib_int, cutoff_freq, fil_osc, freq;

	freq=midicps(midinote);
	f0=exp(vibr*0.035)*freq;

	osc1=Saw.ar(f0*1.0013);
	osc2=Saw.ar(f0*0.998);
	osc3=Saw.ar(f0*0.5);

	cutoff_freq=((cutoff+0.5)*6)*freq;

	fil_osc=BLowPass.ar(in:osc1+osc2+osc3, freq:cutoff_freq.min(20000));
	Out.ar([0,1], amp*fil_osc);}).add;
)

// Synth for chords
(
SynthDef(\harpsi, { |outbus = 0, freq = 440, amp = 0.1, gate = 1|
    var out;
    out = EnvGen.ar(Env.adsr, gate, doneAction: Done.freeSelf) * amp *
        Pulse.ar(freq, 0.25, 0.75);
    Out.ar(outbus, out ! 2);
}).add;    // see below for more on .add
)

// SETTING the instrument as a global variable
(
~instr=Synth(\moog);
)

// setting the note
(
~instr.set(\midinote, 62, \amp, 1);
)

//setting the cutoff
(
~instr.set(\cutoff, 9);
)

(
~instr.set(\amp, 0);
)

// Use this command to start the server
NetAddr("127.0.0.1",57120);

( // RECEIVER 1: PYTHON ONLY
OSCdef('OSCreceiver',
	{
		arg msg;
		var note,amp,dur;

		msg.postln;
		note=msg[1];
		amp=msg[2];
		dur =msg[3];
		~instr.set(\midinote,note, \amp,amp, \dur,dur);

	},
	'/synth_control_melodia',);
)


// Close OSC function
x.free;

// Close server
s.quit;
