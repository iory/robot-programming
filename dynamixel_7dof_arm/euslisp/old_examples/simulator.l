(load "package://dxl_armed_turtlebot/euslisp/dxl-armed-turtlebot.l")
(setq *dxl-armed-turtlebot* (dxl-armed-turtlebot))
(objects (list *dxl-armed-turtlebot*))

(load "package://dxl_armed_turtlebot/euslisp/dxl-armed-turtlebot-interface.l")
(dxl-armed-turtlebot-init)


(do-until-key ()
  (send *dxl-armed-turtlebot* :init-pose)
  (send *irtviewer* :draw-objects)
  (send *ri* :angle-vector (send *dxl-armed-turtlebot* :angle-vector) 4000)
  (send *ri* :wait-interpolation)
  (send *dxl-armed-turtlebot* :reset-pose)
  (send *irtviewer* :draw-objects)
  (send *ri* :angle-vector (send *dxl-armed-turtlebot* :angle-vector) 4000)
  (send *ri* :wait-interpolation)
  )

;; max 50, min -55
;; (send *dxl-armed-turtlebot* :gripper :arm :angle-vector #(50))
(send *ri* :angle-vector (send *dxl-armed-turtlebot* :angle-vector) 1000 :gripper-controller)
(send *ri* :wait-interpolation)
