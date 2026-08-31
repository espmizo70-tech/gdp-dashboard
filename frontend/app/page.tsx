'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, Mic, Type, Video, Play, Pause } from 'lucide-react';

export default function HomePage() {
  const [voices, setVoices] = useState([]);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/voices')
      .then((res) => res.json())
      .then((data) => setVoices(data));
  }, []);

  const playVoice = (url: string, id: string) => {
    if (playingId === id) {
      audio?.pause();
      setPlayingId(null);
    } else {
      if (audio) audio.pause();
      const newAudio = new Audio(url);
      newAudio.play();
      setAudio(newAudio);
      setPlayingId(id);
      newAudio.onended = () => setPlayingId(null);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-white">
      <aside className="w-64 bg-slate-900 border-l border-slate-800 p-6 flex flex-col gap-4">
        <h1 className="text-xl font-bold text-indigo-400 flex items-center gap-2"><Sparkles /> AI Studio</h1>
        <button className="flex items-center gap-2 p-3 bg-indigo-600/20 text-indigo-300 rounded-xl font-semibold"><Mic size={18}/> الأصوات</button>
        <button className="flex items-center gap-2 p-3 hover:bg-slate-800 text-slate-400 rounded-xl font-semibold"><Type size={18}/> التفريغ الصوتي</button>
        <button className="flex items-center gap-2 p-3 hover:bg-slate-800 text-slate-400 rounded-xl font-semibold"><Video size={18}/> إنتاج الفيديو</button>
      </aside>

      <main className="flex-1 p-8 space-y-6">
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
          <h2 className="text-lg font-bold mb-4">🎤 استوديو معاينة الأصوات الاحترافية</h2>
          <div className="grid grid-cols-2 gap-4">
            {voices.map((v: any) => (
              <div key={v.id} className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                <span>{v.name}</span>
                <button onClick={() => playVoice(v.preview_url, v.id)} className="p-3 bg-indigo-600 rounded-full hover:bg-indigo-500">
                  {playingId === v.id ? <Pause size={16} /> : <Play size={16} />}
                </button>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
