var currentSimList = ["Rendering", "Tracking"];
var currentSim = "Rendering";
var currentSimId = 0;
var currentSceneList = [
    "cloth_red_lift",
    "double_stretch_sloth",
    "single_push_rope_1", 
    "single_clift_cloth_3", 
    "double_lift_cloth_1", 
    "single_lift_cloth",    
    "single_lift_sloth",
    "single_lift_cloth_4", 
    "cloth_skirt_2_fold", 
    "weird_package", 
    "double_stretch_zebra",   
    "single_lift_rope"
];
var currentScene = "double_lift_cloth_1";
var currentSceneId = 0;


function ChangeSim(idx){
    var li_list = document.getElementById("sim-view-ul").children;
    for(i = 0; i < li_list.length; i++){
        li_list[i].className = "";
    }
    li_list[idx].className = "active";

    currentSim = currentSimList[idx];
    currentSimId = idx;

    if (currentSim == "Rendering"){
        document.getElementById("demo_video").src = "src/videos/combine_rendering/" + currentScene + '/0_combine.mp4';
    } else {
        document.getElementById("demo_video").src = "src/videos/combine_tracking/" + currentScene + '/0_combine.mp4';
    }
}

function ChangeScene(idx){
    var li_list_row1 = document.getElementById("scene-view-ul-row1").children;
    var li_list_row2 = document.getElementById("scene-view-ul-row2").children;
    
    for(i = 0; i < li_list_row1.length; i++){
        li_list_row1[i].className = "";
    }
    for(i = 0; i < li_list_row2.length; i++){
        li_list_row2[i].className = "";
    }

    if(idx < li_list_row1.length) {
        li_list_row1[idx].className = "active";
    } else {
        li_list_row2[idx - li_list_row1.length].className = "active";
    }

    currentScene = currentSceneList[idx];
    currentSceneId = idx;

    if (currentSim == "Rendering"){
        document.getElementById("demo_video").src = "src/videos/combine_rendering/" + currentScene + '/0_combine.mp4';
    } else {
        document.getElementById("demo_video").src = "src/videos/combine_tracking/" + currentScene + '/0_combine.mp4';
    }

    // currentInst = currentInstDescriptions[idx];
    // currentInstId = idx;

    // document.getElementById("demo-description").innerHTML = currentSceneList[idx];
    
}
