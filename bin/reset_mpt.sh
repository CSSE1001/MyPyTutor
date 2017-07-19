cd /opt/local/share/MyPyTutor/MPT3_CSSE1001/

# Answers
rm -rf data/answers/*

# Feedback
rm -rf data/feedback/*

# Submissions
find data/submissions/ -mindepth 1 -maxdepth 1 -not -name 'tutorial_*' | xargs rm -rf

# User Info
cp /dev/null data/user_info
