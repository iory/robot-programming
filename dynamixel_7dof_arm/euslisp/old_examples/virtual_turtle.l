(load "package://dxl_armed_turtlebot/euslisp/dxl-armed-turtlebot.l")
(setq *dxl-armed-turtlebot* (dxl-armed-turtlebot))
(objects (list *dxl-armed-turtlebot*))

;; get joint-list
;; (send *dxl-armed-turtlebot* :joint-list)

;; get-arm joint instance (arm_joint1~7)
;; (send *dxl-armed-turtlebot* :arm_joint6)

;; (send (send *dxl-armed-turtlebot* :arm_joint6) :joint-angle 30)

;; (send *dxl-armed-turtlebot* :angle-vector)

;; (send *dxl-armed-turtlebot* :angle-vector #f(0.0 0.0 90.0 0.0 90.0 0.0 0.0))

;; (send *dxl-armed-turtlebot* :init-pose)
;; (send *dxl-armed-turtlebot* :reset-pose)
;; (send *dxl-armed-turtlebot* :reset-pose2)
;; (send *dxl-armed-turtlebot* :tuckarm-pose)
;; (send *dxl-armed-turtlebot* :tuckarm-pose2)

;; check end-effector coordinates
;; (send (send *dxl-armed-turtlebot* :arm :end-coords) :draw-on :flush t)

;; (send *dxl-armed-turtlebot* :reset-pose)
;; (send *dxl-armed-turtlebot* :inverse-kinematics
;;       (make-coords :pos (float-vector 370 0 150) :rpy (list 0 (deg2rad 30) (deg2rad 180)))
;;       :debug-view ;; animation-on
;;       :no-message
;;       )

;; (send *dxl-armed-turtlebot* :reset-pose)
;; (send *dxl-armed-turtlebot* :inverse-kinematics
;;       (make-coords :pos (float-vector 400 0 200))
;;       :rotation-axis :z)

;; (send *dxl-armed-turtlebot* :reset-pose)
;; (send *dxl-armed-turtlebot* :inverse-kinematics
;;       (make-coords :pos (float-vector 300 150 150))
;;       :rotation-axis :z
;;       )


;; change convergence test
;; (send *dxl-armed-turtlebot* :inverse-kinematics
;;       (make-coords :pos (float-vector 300 150 150))
;;       :rotation-axis :z
;;       :thre 25 :rthre (deg2rad 25)
;;       ;; (thre 25mm), (rthre 25deg)
;;       )

;; (send *dxl-armed-turtlebot* :inverse-kinematics
;;       (make-coords :pos (float-vector 300 150 150))
;;       :revert-if-fail nil
;;       )
