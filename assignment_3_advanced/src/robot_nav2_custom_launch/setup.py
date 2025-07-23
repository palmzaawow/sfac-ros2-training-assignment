from setuptools import find_packages, setup

package_name = 'robot_nav2_custom_launch'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/nav2_custom_launch.py']),
        ('share/' + package_name + '/config', ['config/nav2_params.yaml', 'config/my_navigate_through_poses.xml' ]),
        ('share/' + package_name + '/maps', ['maps/model03.yaml', 'maps/model03.pgm']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='palmzaawow',
    maintainer_email='palmrock4@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
