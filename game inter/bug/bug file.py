import cv2 as cv
import numpy as np
import mediapipe as mp
import random

LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

bug_img = cv.imread('fly.png', cv.IMREAD_UNCHANGED)
back_img = cv.imread('background.jpg')

# 배경 이미지의 크기
back_height, back_width, _ = back_img.shape

# 벌레 이미지의 크기 조정
new_bug_width = 50
new_bug_height = 54
bug_img = cv.resize(bug_img, (new_bug_width, new_bug_height))

# 벌레 이미지의 랜덤한 위치 설정
bug_x = random.randint(0, back_width - new_bug_width)
bug_y = random.randint(0, back_height - new_bug_height)

mp_face_mesh = mp.solutions.face_mesh

with mp_face_mesh.FaceMesh(max_num_faces=1,
                           refine_landmarks=True,
                           min_detection_confidence=0.5,
                           min_tracking_confidence=0.5
                           ) as face_mesh:
    capture = cv.VideoCapture(0)  # 필요에 따라 적절한 비디오 소스 인덱스로 변경하세요

    if not capture.isOpened():
        print('비디오 캡처를 열 수 없습니다')
        exit()

    while True:
        ret, frame = capture.read()
        frame = cv.flip(frame, 1)
        if not ret:
            print('Error')
            break
        img_h, img_w = frame.shape[:2]
        results = face_mesh.process(frame)
        if results.multi_face_landmarks:
            mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                                    for p in results.multi_face_landmarks[0].landmark])

            gaze_point = (int(mesh_points[0][0]), int(mesh_points[0][1]))  # 눈의 중심 좌표 사용

            for pt in mesh_points:
                cv.circle(frame, pt, 1, (255, 255, 255), -1, cv.LINE_AA)
                pass
            cv.polylines(frame, [mesh_points[LEFT_EYE]], True, (0, 0, 255), 2, cv.LINE_AA)
            cv.polylines(frame, [mesh_points[RIGHT_EYE]], True, (0, 0, 255), 2, cv.LINE_AA)
            # 눈동자
            cv.polylines(frame, [mesh_points[LEFT_IRIS]], True, (0, 255, 0), 2, cv.LINE_AA)
            cv.polylines(frame, [mesh_points[RIGHT_IRIS]], True, (0, 255, 0), 2, cv.LINE_AA)

            (l_cx, l_cy), l_rad = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_rad = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            l_center = np.array([l_cx, l_cy], dtype=np.int32)
            r_center = np.array([r_cx, r_cy], dtype=np.int32)
            cv.circle(frame, l_center, int(l_rad), (0, 255, 0), 2, cv.LINE_AA)
            cv.circle(frame, r_center, int(r_rad), (0, 255, 0), 2, cv.LINE_AA)

            for pt in mesh_points:
                (cx, cy) = pt[0], pt[1]
                cv.circle(frame, [cx, cy], 1, (255, 255, 255), -1, cv.LINE_AA)

            # 배경 이미지 복사
            output = back_img.copy()

            # 배경 이미지의 크기
            back_height, back_width, _ = back_img.shape

            # 프레임 이미지의 크기
            frame_height, frame_width, _ = frame.shape

            # 배경 이미지와 프레임 이미지의 비율 계산
            width_ratio = back_width / frame_width
            height_ratio = back_height / frame_height

            # 눈동자 시점 좌표를 배경 이미지에 맞게 변환
            gaze_point = (int(gaze_point[0] * width_ratio), int(gaze_point[1] * height_ratio))

            # 눈동자 시점 표시
            cv.circle(output, gaze_point, 6, (0, 0, 255), -1)

            # 벌레 이미지를 게임 화면에 표시
            alpha_s = bug_img[:, :, 3] / 255.0  # 벌레 이미지의 알파 채널
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                output[bug_y:bug_y + new_bug_height, bug_x:bug_x + new_bug_width, c] = (
                        alpha_s * bug_img[:, :, c] + alpha_l * output[bug_y:bug_y + new_bug_height,
                                                               bug_x:bug_x + new_bug_width,
                                                               c]
                )

            # 좌표 추출
            x = random.randint(0, back_width - new_bug_width)
            y = random.randint(0, back_height - new_bug_height)
            rand_key = (x, y)

            marker_list = []
            gaze_list = []

            def calibrate_gaze(marker_list, gaze_list, camera_matrix, dist_coeffs):
                # Convert marker and gaze points to numpy arrays
                marker_points = np.array(marker_list, dtype=np.float32)
                gaze_points = np.array(gaze_list, dtype=np.float32)

                # Estimate the pose of the camera relative to the marker
                _, rvec, tvec = cv.solvePnP(marker_points, gaze_points, camera_matrix, dist_coeffs)

                # Convert rotation vector to rotation matrix
                rot_mat, _ = cv.Rodrigues(rvec)

                # Invert rotation matrix and translation vector to get camera pose relative to gaze
                inv_rot_mat = rot_mat.transpose()
                inv_tvec = -inv_rot_mat.dot(tvec)

                # Calculate gaze direction vector
                gaze_dir = inv_rot_mat.dot(np.array([0, 0, 1]))

                # Calculate calibration factor
                calib_factor = inv_tvec[2] / gaze_dir[2]

                # Calculate calibrated gaze points
                calibrated_gaze = []
                for gaze_point in gaze_points:
                    # Calculate 3D position of gaze point
                    gaze_pos_3d = inv_rot_mat.dot(np.array([gaze_point[0], gaze_point[1], 1])) * calib_factor + inv_tvec
                    # Calculate 2D position of gaze point using camera matrix
                    gaze_pos_2d, _ = cv.projectPoints(gaze_pos_3d, rvec, tvec, camera_matrix, dist_coeffs)
                    calibrated_gaze.append(gaze_pos_2d.squeeze().tolist())

                return calibrated_gaze

            # Draw a circle to represent p2 on the background image
            # cv.circle(p2, 5, (0, 0, 255), -1)
            cv.imshow('main', frame)
            # 게임 화면 표시
            cv.imshow('Bug Catching Game', output)

        key = cv.waitKey(1)

        if key == ord('q'):
            break

cv.destroyAllWindows()
