from setuptools import setup, find_packages

setup(
    name="faceauth_ai",
    version="0.1.0",
    description="FaceAuth AI face login system",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "numpy",
        "scikit-learn",
        "streamlit",
    ],
)
