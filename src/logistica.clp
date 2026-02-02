;;; =========================================================
;;; ARCHIVO: logistica.clp
;;; DESCRIPCIÓN: Reglas de negocio para asignación logística
;;; =========================================================

;;; 1. TEMPLATES (Las estructuras de datos)
(deftemplate vehiculo
   (slot matricula)
   (slot tipo (allowed-values moto furgoneta camion))
   (slot carga-max-kg)
   (slot carga-actual (default 0))
   (slot estado (default disponible))
)

(deftemplate pedido
   (slot id)
   (slot peso-kg)
   (slot tipo-carga (allowed-values normal fragil voluminoso refrigerado))
   (slot prioridad (default normal))
)

(deftemplate asignacion
   (slot id-pedido)
   (slot matricula-vehiculo)
   (slot motivo)
)

;;; 2. REGLAS DE ASIGNACIÓN

;;; REGLA CAMIÓN: Para cosas pesadas o voluminosas
(defrule asignar-camion
   ;; Buscamos un pedido pesado O voluminoso
   ?p <- (pedido (id ?pid) (peso-kg ?peso) (tipo-carga ?t))
   (test (or (>= ?peso 500) (eq ?t voluminoso)))
   
   ;; Buscamos un camión con espacio suficiente
   ?v <- (vehiculo (matricula ?m) (tipo camion) (carga-max-kg ?max) (carga-actual ?actual))
   (test (<= (+ ?actual ?peso) ?max))
   =>
   ;; Acción: Crear asignación, actualizar camión y borrar pedido de pendientes
   (assert (asignacion (id-pedido ?pid) (matricula-vehiculo ?m) (motivo "Carga Pesada/Voluminosa")))
   (modify ?v (carga-actual (+ ?actual ?peso)))
   (retract ?p)
   (printout t ">>> [CLIPS] Asignado pedido " ?pid " (" ?peso "kg) al CAMION " ?m crlf)
)

;;; REGLA FURGONETA: Para carga estándar (ni muy grande ni muy pequeña)
(defrule asignar-furgoneta
   ?p <- (pedido (id ?pid) (peso-kg ?peso) (tipo-carga ?t))
   (test (and (> ?peso 10) (< ?peso 500)))
   (test (neq ?t voluminoso))   ;; Exclusividad: No queremos sofás en la furgo
   (test (neq ?t refrigerado))
   
   ?v <- (vehiculo (matricula ?m) (tipo furgoneta) (carga-max-kg ?max) (carga-actual ?actual))
   (test (<= (+ ?actual ?peso) ?max))
   =>
   (assert (asignacion (id-pedido ?pid) (matricula-vehiculo ?m) (motivo "Carga Estandar")))
   (modify ?v (carga-actual (+ ?actual ?peso)))
   (retract ?p)
   (printout t ">>> [CLIPS] Asignado pedido " ?pid " (" ?peso "kg) a FURGONETA " ?m crlf)
)

;;; REGLA MOTO: Para urgencias ligeras
(defrule asignar-moto
   ?p <- (pedido (id ?pid) (peso-kg ?peso) (prioridad urgente))
   (test (<= ?peso 10))
   
   ?v <- (vehiculo (matricula ?m) (tipo moto))
   =>
   (assert (asignacion (id-pedido ?pid) (matricula-vehiculo ?m) (motivo "Urgencia Express")))
   (retract ?p)
   (printout t ">>> [CLIPS] Asignado pedido " ?pid " a MOTO " ?m crlf)
)