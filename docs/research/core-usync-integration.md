# Integración con el uSync base

Fecha: 2026-09-17. **El primer incremento está implementado: Full registra uSync.BackOffice mediante `AdduSync()` y conserva su transferencia protegida.** El objetivo arquitectónico es un complemento del uSync base de código abierto, sin depender de uSync Complete comercial. Esto permite que sus handlers reales de guardado/exportación procesen nuestros cambios; no implica ejecutar el importador genérico de uSync ni soportar automáticamente entidades de terceros.

## Evidencia del repositorio

| Evidencia | Qué demuestra |
|---|---|
| Ferry.Umbraco.csproj, referencias exactas Core y BackOffice 17.4.2 | Dependencia real del uSync público; ninguna referencia a Complete |
| UmbracoBuilderExtensions.AddFerryUmbracoFull | Ejecuta `AdduSync()` de forma idempotente y registra nuestros stores/servicios; el adapter de texto restringido usa una ruta propia |
| UmbracoSchemaTransfer | Resuelve `SyncSerializerCollection.GetSerializer<T>()`; usa serialización, deserialización, segunda pasada y guardado públicos para cuatro familias de esquema |
| UmbracoFullSyncStore | Usa `SyncValueMapperCollection` para valores y dependencias, pero mantiene asignación de identidades, lotes y guardado de borradores propios |
| PortableEditorPolicy y FerryEditorOptions | Un mapper externo necesita cumplir nuestra política y validaciones; no equivale a soportar cualquier handler o nueva entidad |

Ahora registramos los handlers del paquete base; no creamos un handler de importación Ferry ni invocamos el pipeline genérico import/report para nuestros borradores. Los guardados nativos generan notificaciones del CMS, y los handlers base pueden exportarlos con sus notificaciones auténticas de exportación. **Esto no equivale a las notificaciones de importación de uSync.** La configuración del paquete base sigue gobernando sus archivos y suscriptores.

La muestra y el consumer NuGet incluyen además el paquete público completo `uSync` 17.4.2, con su UI. La regresión de 19 escenarios pasó junto a esa instalación; las 166 pruebas .NET incluyen registro real e idempotencia. Los resultados detallados de la integración están en verificación. El composer nativo puede activar base uSync aunque no se habilite el transporte Ferry; instalar el addon no deshabilita la configuración del sitio.

## Qué aportan las cuatro páginas de extensibilidad

La revisión principal comprobó las páginas canónicas actuales (`Current (v17+)`) y su contenido en el commit oficial [1223bbcc296ff917f919666f5be4d1cf3fb4c8b5](https://github.com/Jumoo/jumoo-docs/tree/1223bbcc296ff917f919666f5be4d1cf3fb4c8b5). La caché web muestra versiones contradictorias; los ejemplos no fijan por sí solos las firmas disponibles en 17.4.2.

- [Value mappers](https://docs.jumoo.co.uk/usync/uSync/extending/valuemappers/): conversión de valores y descubrimiento de dependencias son contratos reutilizables. Una referencia GUID estable no elimina la necesidad de descubrir los elementos relacionados.
- [Notifications](https://docs.jumoo.co.uk/usync/uSync/extending/events/): hay eventos de lote y por elemento; los previos por elemento permiten cancelar. Debemos respetar el pipeline que realmente se ejecute, sin emitir eventos artificiales para aparentar compatibilidad.
- [Detecting](https://docs.jumoo.co.uk/usync/uSync/extending/detecting/): distingue origen y pausa mediante estado de notificación, relevante también para procesos en background. Describe mantener la carpeta uSync predeterminada actualizada tras una transferencia; no recomienda omitir indiscriminadamente las notificaciones de negocio.
- [Root folders](https://docs.jumoo.co.uk/usync/uSync/extending/rootfolders/): las carpetas configuradas y adicionales tienen orden y reglas de combinación. El staging privado no debe convertirse accidentalmente en una raíz permanente ni alterar la precedencia de archivos del sitio.

## Decisión y límites

Los contratos públicos ya revisados sustentan este primer incremento. Por cada nueva familia, elegir la integración con serializers, mappers y handlers del uSync base. Conservar nuestro transporte, aprobación, assets y recuperación, y los controles de borrador/publicación cuando un importador genérico tenga otros efectos. La compatibilidad con extensiones de terceros se declara por contratos probados, nunca por la mera presencia de un paquete.

La etapa **B-1** del plan principal exige dos sitios con el uSync base instalado: configuración de handlers, cancelación, consistencia de carpetas, ausencia de bucles y una extensión externa real. No se atribuye origen de importación uSync al guardado propio: esa marca pertenece al scope interno del importador y no tiene un equivalente público que debamos simular.

Los cuatro escenarios específicos ya verifican exportaciones reales, valores XML actualizados, repetición sin cambios, handler deshabilitado, selección con un mapper externo y ambas cancelaciones. Los callbacks observados no están pausados. La ausencia de notificaciones/estado de importación sintéticos se comprobó en código; no se afirma compatibilidad general con el origen del importador ni con handlers arbitrarios.
