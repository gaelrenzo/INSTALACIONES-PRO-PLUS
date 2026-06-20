from __future__ import annotations

from electra_core.interfaces.puertos import ExportadorBIM
from electra_core.modelos.topologia import RedElectrica


class ExportadorIFC(ExportadorBIM):
    def exportar_ifc(self, red: RedElectrica, ruta: str) -> str:
        try:
            import ifcopenshell
            import ifcopenshell.api
        except ImportError:
            msg = "ifcopenshell no instalado. Usar: pip install electra_core[bim]"
            raise ImportError(msg)

        model = ifcopenshell.api.run("project.create_file")
        project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name=red.nombre_proyecto)

        context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
        body_context = ifcopenshell.api.run("context.add_context", model, context_type="Model",
            context_identifier="Body", target_view="MODEL_VIEW", parent=context)

        site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
        building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding", name="Building")
        ifcopenshell.api.run("aggregate.assign_object", model, products=[building], relating_object=site)
        ifcopenshell.api.run("aggregate.assign_object", model, products=[site], relating_object=project)

        dist_system = ifcopenshell.api.run("root.create_entity", model,
            ifc_class="IfcDistributionSystem", name="ElectricalSystem")
        dist_system.PredefinedType = "ELECTRICAL"

        for tablero in red.tableros:
            tablero_ifc = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcSwitchingDevice", name=tablero.nombre)
            ifcopenshell.api.run("group.assign_group", model, products=[tablero_ifc], group=dist_system)

        model.write(ruta)
        return ruta
