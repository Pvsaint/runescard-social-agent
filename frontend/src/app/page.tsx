"use client";

import { useState, useEffect } from "react";
import {
  SendHorizontal,
  Sparkles,
  Twitter,
  MessageCircle,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  Settings,
  Copy,
} from "lucide-react";

export default function Home() {
  const [platforms, setPlatforms] = useState<string[]>([]);
  const [postTypes, setPostTypes] = useState<string[]>([]);

  const [selectedPlatform, setSelectedPlatform] = useState("twitter");
  const [selectedType, setSelectedType] = useState("random");
  const [hint, setHint] = useState("");

  const [draft, setDraft] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Fetch config on load
  useEffect(() => {
    fetch("/api/config")
      .then((r) => r.json())
      .then((data) => {
        setPlatforms(data.platforms || ["twitter", "farcaster"]);
        setPostTypes(data.post_types || ["random"]);
      })
      .catch((err) => {
        console.error("Failed to fetch config:", err);
        setError(
          "Could not connect to the Python backend (is uvicorn running on port 8000?)",
        );
      });
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError("");
    setSuccess("");

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform: selectedPlatform,
          post_type: selectedType,
          extra_hint: hint,
        }),
      });

      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "Failed to generate content");
      }

      const data = await res.json();
      setDraft(data.text);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = async () => {
    if (!draft.trim()) return;

    setError("");
    try {
      await navigator.clipboard.writeText(draft);
      setIsCopied(true);
      setSuccess("Draft copied to clipboard!");
      setTimeout(() => {
        setIsCopied(false);
        setSuccess("");
      }, 3000);
    } catch (err: any) {
      setError("Failed to copy text. Please select and copy manually.");
    }
  };

  const handlePublish = async () => {
    if (!draft.trim()) return;

    setIsPublishing(true);
    setError("");

    try {
      const res = await fetch("/api/publish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform: selectedPlatform,
          text: draft,
        }),
      });

      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "Failed to publish content");
      }

      setSuccess(`Successfully posted to ${selectedPlatform}!`);
      setDraft(""); // Clear after successful post
      setHint("");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <main className="min-h-screen p-6 md:p-12 max-w-5xl mx-auto flex flex-col gap-8 relative z-10">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent flex items-center gap-3">
            <Sparkles className="text-blue-400 w-8 h-8" />
            RunesCard AI Agent
          </h1>
          <p className="text-slate-400 mt-2">
            Autonomous Social Media Content Orchestrator
          </p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700/50 text-sm">
            <div
              className={`w-2 h-2 rounded-full ${platforms.length > 0 ? "bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.5)]" : "bg-rose-400"}`}
            />
            Backend {platforms.length > 0 ? "Connected" : "Offline"}
          </div>
        </div>
      </header>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      {success && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
          <p>{success}</p>
        </div>
      )}

      <div className="grid md:grid-cols-5 gap-6">
        {/* Left Column: Controls */}
        <div className="md:col-span-2 flex flex-col gap-6">
          <div className="glass-panel rounded-2xl p-6 flex flex-col gap-5 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full blur-3xl" />

            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Settings className="w-5 h-5 text-slate-400" />
              Configuration
            </h2>

            {/* Platform Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">
                Target Platform
              </label>
              <div className="grid grid-cols-2 gap-3">
                {platforms.map((p) => (
                  <button
                    key={p}
                    onClick={() => setSelectedPlatform(p)}
                    className={`flex items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                      selectedPlatform === p
                        ? "bg-blue-500/20 border-blue-500/50 text-blue-300"
                        : "bg-slate-800/40 border-slate-700/50 text-slate-400 hover:bg-slate-800"
                    }`}
                  >
                    {p === "twitter" ? (
                      <Twitter className="w-4 h-4" />
                    ) : (
                      <MessageCircle className="w-4 h-4" />
                    )}
                    <span className="capitalize">{p}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Post Type Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">
                Post Theme
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg p-3 text-slate-200 outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 appearance-none transition-all"
              >
                {postTypes.map((t) => (
                  <option key={t} value={t}>
                    {t.replace("_", " ")}
                  </option>
                ))}
              </select>
            </div>

            {/* Hint / Hook */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">
                Extra Context (Optional)
              </label>
              <textarea
                value={hint}
                onChange={(e) => setHint(e.target.value)}
                placeholder="E.g., We just hit 10k users today!"
                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg p-3 text-slate-200 outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all resize-none h-24 placeholder:text-slate-600"
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || platforms.length === 0}
              className="mt-2 w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 text-white font-medium py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(37,99,235,0.2)] hover:shadow-[0_0_25px_rgba(37,99,235,0.4)] relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
              {isGenerating ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Generating Draft...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Draft New Post
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Preview & Publish */}
        <div className="md:col-span-3">
          <div className="glass-panel rounded-2xl p-6 h-full flex flex-col gap-4 relative">
            <h2 className="text-xl font-semibold flex items-center justify-between">
              Draft Preview
              <span
                className={`text-xs px-2 py-1 rounded bg-slate-800 border ${
                  draft.length > (selectedPlatform === "twitter" ? 280 : 320)
                    ? "border-rose-500/50 text-rose-400"
                    : "border-slate-700 text-slate-400"
                }`}
              >
                {draft.length} / {selectedPlatform === "twitter" ? 280 : 320}{" "}
                chars
              </span>
            </h2>

            <div className="flex-1 rounded-xl bg-slate-900/50 border border-slate-700/50 relative group">
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Your generated post will appear here. You can manually edit it before publishing."
                className="w-full h-full min-h-[300px] bg-transparent p-5 text-lg text-slate-200 outline-none resize-none placeholder:text-slate-700 leading-relaxed"
              />
            </div>

            <div className="flex justify-end pt-2 gap-4">
              <button
                onClick={handleCopy}
                disabled={!draft || isGenerating}
                className="bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:hover:bg-slate-700 text-slate-200 font-medium py-3 px-6 rounded-lg transition-all flex items-center gap-2 shadow-[0_0_10px_rgba(0,0,0,0.2)]"
              >
                {isCopied ? (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-5 h-5" />
                    Copy
                  </>
                )}
              </button>
              <button
                onClick={handlePublish}
                disabled={!draft || isPublishing || isGenerating}
                className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:hover:bg-emerald-600 text-white font-medium py-3 px-8 rounded-lg transition-all flex items-center gap-2 shadow-[0_0_15px_rgba(5,150,105,0.3)] hover:shadow-[0_0_20px_rgba(5,150,105,0.5)]"
              >
                {isPublishing ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <SendHorizontal className="w-5 h-5" />
                    Publish Live
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
