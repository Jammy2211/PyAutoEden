echo "Setting up Environment variables."
export PROJECT_NAME=VIS_CTI
export BUILD_PATH=build_eden
export PPO_PATH=../../PPOEuclid

echo "Removing pytest cache and pyc files"
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

echo "Removing old PE from PPOEuclid"
rm -rf $PPO_PATH/$PROJECT_NAME/*

echo "Copying new build_eden project to PPOEuclid"
cp -r $BUILD_PATH/$PROJECT_NAME/* $PPO_PATH/$PROJECT_NAME

echo "Committing project and pushing to gitlab"
cd $PPO_PATH/$PROJECT_NAME
git add -u
git add -f -A
git commit -m "testing gitlab has all files"
git push

PyAutoEden