import Link from "next/link";
import { Button } from "@/components/ui/button";
import { PenTool, ArrowRight, Zap, FileText, Calculator } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <div className="flex items-center gap-2 font-bold text-xl">
            <PenTool className="h-6 w-6 text-primary" />
            Electra
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Iniciar sesión</Button>
            </Link>
            <Link href="/login">
              <Button>Registrarse</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <section className="mx-auto max-w-6xl px-4 py-24 text-center">
          <h1 className="text-5xl font-bold tracking-tight mb-4">
            Ingeniería Eléctrica{" "}
            <span className="text-primary">Asistida por IA</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
            Calcula, diseña y documenta instalaciones eléctricas residenciales
            según normativa CNE Perú. De tu croquis al expediente técnico.
          </p>
          <Link href="/login">
            <Button size="lg" className="gap-2">
              Comenzar <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </section>

        <section className="border-t py-16">
          <div className="mx-auto max-w-6xl px-4 grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: Calculator, title: "Cálculos CNE", desc: "Máxima demanda, conductores, protecciones y caída de tensión según CNE Perú." },
              { icon: PenTool, title: "Planos CAD", desc: "Generación automática de planos DXF con simbología DGE." },
              { icon: FileText, title: "Expediente Técnico", desc: "Documento LaTeX completo: memoria, cálculos, metrados y presupuesto." },
            ].map((feature) => {
              const Icon = feature.icon;
              return (
                <div key={feature.title} className="flex flex-col items-center text-center p-6 rounded-xl border bg-card">
                  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.desc}</p>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      <footer className="border-t py-6 text-center text-sm text-muted-foreground">
        Electra v2.0 — Motor de ingeniería eléctrica automatizada
      </footer>
    </div>
  );
}
