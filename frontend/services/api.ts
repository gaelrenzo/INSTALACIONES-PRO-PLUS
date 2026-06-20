const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  proyectos: {
    listar: () => request<any[]>("/proyectos/"),
    crear: (data: any) => request<any>("/proyectos/", { method: "POST", body: JSON.stringify(data) }),
    obtener: (id: string) => request<any>(`/proyectos/${id}`),
    eliminar: (id: string) => request<void>(`/proyectos/${id}`, { method: "DELETE" }),
  },
  calcular: {
    ejecutar: (proyecto_id: string) =>
      request<any>("/calcular/", { method: "POST", body: JSON.stringify({ proyecto_id }) }),
  },
  cad: {
    generar: (proyecto_id: string, formato = "dxf") =>
      request<any>("/generar/dxf", { method: "POST", body: JSON.stringify({ proyecto_id, formato }) }),
  },
  cotizar: {
    ejecutar: (proyecto_id: string) =>
      request<any>("/cotizar/", { method: "POST", body: JSON.stringify({ proyecto_id }) }),
  },
  expediente: {
    generar: (proyecto_id: string, compilar_pdf = true) =>
      request<any>("/expediente/", { method: "POST", body: JSON.stringify({ proyecto_id, compilar_pdf }) }),
  },
};
