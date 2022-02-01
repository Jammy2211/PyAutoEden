echo "Setting up Environment variables."
export PROJECTS_PATH=/home/user/Work/Projects
export PYAUTO_PATH=/home/user/Work/PyAuto

echo "Removing old PE from Work/Projects"
rm -rf $PROJECTS_PATH/SHE_ArCTIC/*

echo "Coping new PE to Work/Projects"
cp -r $PYAUTO_PATH/SHE_ArCTIC $PROJECTS_PATH
sudo chmod -R 777 $PROJECTS_PATH/SHE_ArCTIC

git add -f $PROJECTS_PATH/.jenkinsFile

echo "Making Project"
cd $PROJECTS_PATH/SHE_ArCTIC
make purge
make
make install
cd $PYAUTO_PATH/SHE_ArCTIC