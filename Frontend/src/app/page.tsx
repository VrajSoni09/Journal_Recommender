"use client"

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { BookOpen } from "lucide-react";

export default function Page() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to dashboard after 2 seconds
    const timer = setTimeout(() => {
      router.push("/dashboard");
    }, 2000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-blue-950 to-emerald-950 relative overflow-hidden flex items-center justify-center">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-96 h-96 bg-gradient-to-r from-blue-500/30 to-cyan-500/30 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-10 w-[500px] h-[500px] bg-gradient-to-r from-emerald-500/30 to-teal-500/30 rounded-full blur-3xl animate-float-delayed" />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-gradient-to-r from-blue-600/25 to-green-600/25 rounded-full blur-3xl animate-pulse-slow" />
      </div>

      {/* Logo Animation */}
      <div className="relative z-10 flex flex-col items-center gap-8 animate-fade-in">
        {/* Logo */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-full blur-3xl opacity-50 animate-pulse-slow"></div>
          <div className="relative bg-gradient-to-br from-emerald-500 to-cyan-500 p-8 rounded-3xl shadow-2xl transform transition-all duration-1000 hover:scale-110">
            <BookOpen className="w-24 h-24 text-white" />
          </div>
        </div>

        {/* Logo Text */}
        <div className="text-center space-y-4">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-emerald-400 via-cyan-400 to-emerald-400 bg-clip-text text-transparent animate-gradient">
            ResearchHub
          </h1>
          <p className="text-xl text-gray-300 animate-fade-in-delay">
            AI-Powered Journal Recommendations
          </p>
        </div>

        {/* Loading indicator */}
        <div className="flex gap-2 mt-8">
          <div className="w-3 h-3 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
          <div className="w-3 h-3 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
          <div className="w-3 h-3 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
        </div>
      </div>
    </div>
  );
}
