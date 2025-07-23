from setuptools import find_packages, setup

package_name = 'robot_action'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'rclpy', 'robot_interfaces'],
    zip_safe=True,
    maintainer='palmzaawow',
    maintainer_email='palmrock4@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'parking_action_server = robot_action.parking_action_server:main',
        ],
    },
)
