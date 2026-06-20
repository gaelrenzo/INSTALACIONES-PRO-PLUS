"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/services/api";
import { supabase } from "@/lib/supabase";
import {
  Calculator,
  PenTool,
  DollarSign,
  FileText,
  ArrowLeft,
  Loader2,
  Download,
  CheckCircle,
} from "lucide-react";

type ActionType = "calcular" | "cad" | "cotizar" | "expediente";

export default function ProyectoDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [proyecto, setProyecto] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<ActionType | null>(null);
  const [results, setResults] = useState<Record<string, any>>({});

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      if (!data?.user) return router.push("/login");
      cargarProyecto();
    });
  }, [id]);

  async function cargarProyecto() {
    try {
      const data = await api.proyectos.obtener(id);
      setProyecto(data);
    } catch {
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  }

  async function ejecutar(accion: ActionType) {
    setActionLoading(accion);
    try {
      let result;
      switch (accion) {
        case "calcular":
          result = await api.calcular.ejecutar(id);
          break;
        case "cad":
          result = await api.cad.generar(id);
          break;
        case "cotizar":
          result = await api.cotizar.ejecutar(id);
          break;
        case "expediente":
          result = await api.expediente.generar(id);
          break;
      }
      setResults((prev) => ({ ...prev, [accion]: result }));
      cargarProyecto();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  }

  const actions: { key: ActionType; label: string; icon: any; desc: string }[] = [
    { key: "calcular", label: "Calcular", icon: Calculator, desc: "Máxima demanda, conductores y protecciones" },
    { key: "cad", label: "Generar CAD", icon: PenTool, desc: "Planos DXF con simbología DGE" },
    { key: "cotizar", label: "Cotizar", icon: DollarSign, desc: "BOM y comparativa de proveedores" },
    { key: "expediente", label: "Expediente", icon: FileText, desc: "Documento LaTeX completo + PDF" },
  ];

  if (loading) return <div className="flex items-center justify-center h-64 text-muted-foreground">Cargando...</div>;
  if (!proyecto) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{proyecto.nombre}</h1>
            <Badge variant={proyecto.estado === "completado" ? "success" : "secondary"}>
              {proyecto.estado}
            </Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {actions.map(({ key, label, icon: Icon, desc }) => {
          const isDone = results[key] || (proyecto.estado === "completado" && key !== "calcular");
          return (
            <Card key={key}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  {label}
                  {isDone && <CheckCircle className="h-4 w-4 text-emerald-500 ml-auto" />}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">{desc}</p>
                <Button
                  className="w-full"
                  variant={isDone ? "outline" : "default"}
                  onClick={() => ejecutar(key)}
                  disabled={actionLoading === key}
                >
                  {actionLoading === key ? (
                    <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Procesando...</>
                  ) : isDone ? (
                    <><Download className="h-4 w-4 mr-2" /> Descargar</>
                  ) : (
                    `Ejecutar ${label}`
                  )}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
