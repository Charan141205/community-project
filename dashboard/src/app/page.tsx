import Link from "next/link";
import { ShieldAlert, Users, Radio, Navigation, ArrowRight, Activity, CloudRain } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-950 via-slate-900 to-black text-white flex flex-col justify-between p-6 md:p-12">
      {/* Top Banner */}
      <div className="max-w-6xl mx-auto w-full flex items-center justify-between border-b border-gray-800 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">flood-ews</h1>
            <p className="text-xs text-gray-400">Smart Community Flood & Urban Drainage Early Warning System</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-semibold text-emerald-400">Basin Live: Swarnamukhi River, Tirupati</span>
        </div>
      </div>

      {/* Hero Section */}
      <div className="max-w-4xl mx-auto w-full my-auto text-center py-12 space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold">
          <Radio className="w-3.5 h-3.5 animate-pulse" />
          Real-Time IoT Drainage Telemetry & Floodgate Automation
        </div>

        <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
          Protecting Communities from Flash Floods & Sewer Backflow
        </h2>

        <p className="text-base md:text-lg text-gray-300 max-w-2xl mx-auto leading-relaxed">
          Simulated ESP32 sensor nodes measure storm drain water depth and rainfall rates,
          autonomously actuate floodgates to prevent urban backflow, dispatch multilingual alerts
          (Telugu, Hindi, English), and compute dynamic evacuation routes avoiding inundated streets.
        </p>

        {/* Portals */}
        <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto pt-6 text-left">
          {/* Public Portal */}
          <Link
            href="/public"
            className="group p-6 rounded-2xl bg-surface/70 hover:bg-surface border border-border/80 hover:border-blue-500/50 shadow-xl transition-all duration-300 flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                <Users className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white group-hover:text-blue-400 transition">
                Community Public View
              </h3>
              <p className="text-xs text-gray-400 mt-2 leading-relaxed">
                Live interactive flood hazard map, citizen alert opt-in form (SMS & WhatsApp in Telugu, Hindi & English),
                and click-to-route evacuation paths to relief shelters.
              </p>
            </div>
            <div className="mt-6 flex items-center gap-2 text-xs font-bold text-emerald-400 group-hover:translate-x-1 transition">
              Launch Public Map <ArrowRight className="w-4 h-4" />
            </div>
          </Link>

          {/* Operator Portal */}
          <Link
            href="/ops"
            className="group p-6 rounded-2xl bg-surface/70 hover:bg-surface border border-border/80 hover:border-amber-500/50 shadow-xl transition-all duration-300 flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center mb-4">
                <Radio className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white group-hover:text-amber-400 transition">
                Operator Command Center
              </h3>
              <p className="text-xs text-gray-400 mt-2 leading-relaxed">
                Full-featured control dashboard with floodgate actuation overrides, live risk engine telemetry,
                sensor health diagnostics, and audit logs.
              </p>
            </div>
            <div className="mt-6 flex items-center gap-2 text-xs font-bold text-amber-400 group-hover:translate-x-1 transition">
              Launch Operator Ops <ArrowRight className="w-4 h-4" />
            </div>
          </Link>
        </div>
      </div>

      {/* Feature Highlights Footer */}
      <div className="max-w-6xl mx-auto w-full grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-gray-800 text-xs text-gray-400">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          <span>3-Min Rise Rate Hysteresis</span>
        </div>
        <div className="flex items-center gap-2">
          <CloudRain className="w-4 h-4 text-blue-400" />
          <span>0-100 mm/h Rain Sensing</span>
        </div>
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-400" />
          <span>Local ESP32 Autonomy Failsafe</span>
        </div>
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-purple-400" />
          <span>300m Flood Avoidance Routing</span>
        </div>
      </div>
    </main>
  );
}
