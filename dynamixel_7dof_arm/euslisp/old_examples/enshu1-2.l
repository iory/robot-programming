(load "package://dxl_armed_turtlebot/euslisp/dxl-armed-turtlebot.l")
(load "package://dxl_armed_turtlebot/euslisp/dxl-armed-turtlebot-interface.l")
(dxl-armed-turtlebot-init)
(setq *dxl-armed-turtlebot* (dxl-armed-turtlebot))
;;(defvar *dxl-armed-turtlebot* (dxl-armed-turtlebot))
;;(load "package://daisya_euslisp_tutorials/euslisp/daisya-ik.l")
(objects (list *dxl-armed-turtlebot*))


;;(ros::load-ros-manifest "dynamixel_msgs") ;; dynamixelのメッセージを用いるためのload設定
(ros::roseus "joystick_arm") ;; ros initを行う

(defun ik-demo-my
  (&key (step 10)        ;;stepは一回のループで目標を動かす距離
        (use-base nil)  ;;車輪を使ってIKを解くかどうか
        (robot *daisya*)
        (w "0")
        )
  ;;逆運動学が解きやすい初期姿勢に変更
  ;;(send robot :reset-pose)
  ;; (when (boundp '*ri*)
  ;;   (send *ri* :angle-vector (send robot :angle-vector) 5000)
  ;;   (send *ri* :wait-interpolation))
  (objects (list robot))

  ;;
  ;;'e'を押すまで続ける
  (warn ";; if stop, then enter e~%")
  (warn ";;  h:left, j:down, k:up, l:right, f:forward, b:back~%")
  (let (goal-endcoords ll)
    ;;もし腕しか使わない場合はlinklistをあらかじめ用意しておく
    ;;目標座標を作成する(デフォルトは、台車の手先位置と同じにする)
    (setq goal-endcoords
          (make-cascoords :pos (send (send robot :arm :end-coords :copy-worldcoords) :worldpos)))
      ;;文字によって操作を変える
    (print w)
    (cond
     ;; ((equal w "e")
     ;;  (
     ;;   (send robot :reset-pose)
     ;;   ))
     ((equal w "h")  ;;左へ動かす
      (send goal-endcoords :locate (float-vector 0 step 0)))
     ((equal w "j")  ;;下へ動かす
      (send goal-endcoords :locate (float-vector 0 0 (* -1 step))))
     ((equal w "k")  ;;上へ動かす
      (send goal-endcoords :locate (float-vector 0 0 step)))
     ((equal w "l")  ;;右へ動かす
      (send goal-endcoords :locate (float-vector 0 (* -1 step) 0)))
     ((equal w "f")  ;;前へ動かす
      (send goal-endcoords :locate (float-vector step 0 0)))
     ((equal w "b")  ;;後へ動かす
      (send goal-endcoords :locate (float-vector (* -1 step) 0 0)))
     ((not w)) ;;何も入れられなければ何もしない
     (t
        (warn ";; no such command~%")
        (warn ";; if stop, then enter e~%")
        (warn ";;  h:left, j:down, k:up, l:right, f:forward, b:back~%")
        ))
    ;;目標値end-coordsに向かって逆運動学を解いて、動かす
    ;;  inverse-kinematicsという逆運動学をとくmethodを呼び出す。
    (print goal-endcoords)
    (send robot :inverse-kinematics goal-endcoords :rotation-axis nil :debug-view nil :link-list ll)

    (send *irtviewer* :objects (list robot goal-endcoords))
    (send *irtviewer* :draw-objects)
    (when (boundp '*ri*)
      (send *ri* :angle-vector (send robot :angle-vector) 500)
      (send *ri* :wait-interpolation)
      )
    )
  )


(defun dxl-state-cb
  (msg)
  (cond ((eq (elt (send msg :buttons) 13) 1)
         (progn
           (print (send msg :buttons))
           (send *dxl-armed-turtlebot* :gripper :arm :angle-vector #f(50))
           (send *ri* :angle-vector (send *dxl-armed-turtlebot* :angle-vector) 1000 :gripper-controller)
           (send *ri* :wait-interpolation :gripper-controller)
           (send *ri* :start-grasp)
           )
         )
        ((eq (elt (send msg :buttons) 12) 1)
         (progn
           (print (send msg :buttons))
           (send *dxl-armed-turtlebot* :gripper :arm :angle-vector #f(0))
           (send *ri* :angle-vector (send *dxl-armed-turtlebot* :angle-vector) 1000 :gripper-controller)
           (send *ri* :wait-interpolation :gripper-controller)
           (send *ri* :start-grasp)
           )
         )
        ((eq (elt (send msg :buttons) 4) 1)
         (progn
           (print "go up")
           (ik-demo-my :robot *dxl-armed-turtlebot* :w "k")
           )
         )
        ((eq (elt (send msg :buttons) 7) 1)
         (progn
           (print "go left")
           (ik-demo-my :robot *dxl-armed-turtlebot* :w "h")
           )
         )
        ((eq (elt (send msg :buttons) 6) 1)
         (progn
           (print "go down")
           (ik-demo-my :robot *dxl-armed-turtlebot* :w "j")
           )
         )
        ((eq (elt (send msg :buttons) 5) 1)
         (progn
           (print "go right")
           (ik-demo-my :robot *dxl-armed-turtlebot* :w "l")
           )
         )
        ((eq (elt (send msg :buttons) 7) 1)
         (progn
           (print "go forward")
           (ik-demo-my :robot *dxl-armed-turtlebot* :w "l")
           )
         )
        ((eq (elt (send msg :buttons) 0) 1)
         (progn
           (print "reset")
           (ik-demo-my :robot *dxl-armed-turtlebot* :w "e")
           )
         )
        (t
         (format t "noinput")
         )
        )
  )

;;   subscriberの登録
(ros::subscribe "/joy" ;; subscribeしたいtopic名
                  sensor_msgs::Joy ;; topicの型名
                  #'dxl-state-cb) ;; コールバック関数の設

(do-until-key
 (ros::spin-once)
 ;;(sys::gc)
)
