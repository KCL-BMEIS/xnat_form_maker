#actions boes need to be changed to restrict the project
#if($project.contains("$pr"))
#place in project base folder
pr=$1
replace="#if(\$project.contains(\"$pr\") "

echo "$pr $orig $replace"
find . -type f -name "*_assessors.vm" -exec sed -i  "1s/^/$replace/g" {} \;
find . -type f -name "*_assessors.vm" -exec  sed -i  "$ s!</li>!#end!g" {} \;
./gradlew clean jar
cp ./build/libs/*.jar ./


