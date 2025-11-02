from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'jsk_enshu_recognition'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'requirements.txt']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'scripts'), glob('scripts/*')),
    ],
    install_requires=[
        'setuptools',
        # Note: mediapipe and tensorflow require manual installation
        # Run: pip3 install --user -r requirements.txt
        # or: ./scripts/install_dependencies.sh
    ],
    zip_safe=True,
    maintainer='iory',
    maintainer_email='ab.ioryz@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hand_pose_estimation = jsk_enshu_recognition.hand_pose_estimation:main',
            'gesture_recognition = jsk_enshu_recognition.gesture_recognition:main',
            'face_recognition = jsk_enshu_recognition.face_recognition:main',
            'people_pose_estimation = jsk_enshu_recognition.people_pose_estimation:main',
            'skeleton_with_depth = jsk_enshu_recognition.skeleton_with_depth:main',
        ],
    },
)
