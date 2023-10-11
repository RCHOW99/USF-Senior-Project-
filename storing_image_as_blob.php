<!DOCTYPE html>
<html>
<head>
<title>Title of the document</title>
</head>

<body>
<form name="form1" action="" method="post" enctype="multipart/form-data">
<input type="file" name="image"><input type="submit" name="submit" value="Upload">
</form>

<?php 
//The test table storing the images is image_blob_test_db
include 'connect.php'; 
if(isset($_POST['submit'])){
// Image data is the binary string data of the image using get file contents function, it is retrivated from the file inputed in the form, which has the name "image"
$imageData = addslashes(file_get_contents($_FILES['image']['tmp_name']));
//Add slashes function added becuase sql would try to execute image file contents as sql code. 
// Image name is the name, its is retrivated from the file inputed in the form, which has the name "image"
$imageName = ($_FILES['image']['name']);
$sql="insert into image_blob_test_db values('$imageName','$imageData')";
mysqli_query($con,$sql);
}
?>
</body>

</html>