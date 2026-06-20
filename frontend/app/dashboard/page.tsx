"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/services/api";
import { Plus, FolderOpen, Calculator, FileText, DollarSign } from "lucide-react";

const estadoColors: Record<string, "default" | "secondary" | "success" | "warning" | "outline"> = {
  borrador: "secondary",
  arquitectura: "warning",
  diseno: "warning",
  calculado: "success",
  completado: "success",
};

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [proyectos, setProyectos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewForm, setShowNewForm] = useState(false);
  const [newName, setNewName] = useState("");

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      if (!data?.user) return router.push("/login");
      setUser(data.user);
      loadProyectos();
    });
  }, []);

  async function loadProyectos() {
    try {
      const data = await api.proyectos.listar();
      setProyectos(data);
    } catch {
      setProyectos([]);
    } finally {
      setLoading(false);
    }
  }

  async function crearProyecto() {
    if (!newName.trim()) return;
    try {
      await api.proyectos.crear({ nombre: newName.trim() });
      setNewName("");
      setShowNewForm(false);
      loadProyectos();
    } catch (e) {
      console.error(e);
    }
  }

  if (loading) return <div className="flex items-center justify-center h-64 text-muted-foreground">Cargando...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Mis Proyectos</h1>
          <p className="text-muted-foreground">{proyectos.length} proyectos registrados</p>
        </div>
        <Button onClick={() => setShowNewForm(!showNewForm)} className="gap-2">
          <Plus className="h-4 w-4" /> Nuevo Proyecto
        </Button>
      </div>

      {showNewForm && (
        <Card>
          <CardContent className="flex gap-2 pt-6">
            <input
              className="flex h-9 w-full max-w-sm rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              placeholder="Nombre del proyecto"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && crearProyecto()}
            />
            <Button onClick={crearProyecto}>Crear</Button>
            <Button variant="ghost" onClick={() => setShowNewForm(false)}>Cancelar</Button>
          </CardContent>
        </Card>
      )}

      {proyectos.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center py-16 text-muted-foreground">
            <FolderOpen className="h-12 w-12 mb-4" />
            <p className="text-lg mb-2">No tienes proyectos aún</p>
            <p className="text-sm mb-4">Crea tu primer proyecto para comenzar</p>
            <Button onClick={() => setShowNewForm(true)}>Crear proyecto</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {proyectos.map((p) => (
            <Card
              key={p.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push(`/proyectos/${p.id}`)}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-base">{p.nombre}</CardTitle>
                  <Badge variant={estadoColors[p.estado] || "secondary"}>{p.estado}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 text-sm text-muted-foreground">
                  {p.estado !== "borrador" && (
                    <>
                      <span className="flex items-center gap-1"><Calculator className="h-3 w-3" /> OK</span>
                      <span className="flex items-center gap-1"><DollarSign className="h-3 w-3" /> OK</span>
                      <span className="flex items-center gap-1"><FileText className="h-3 w-3" /> OK</span>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
