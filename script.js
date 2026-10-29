const pages = ["dashboard","crops","analyze","risk","advice","stores"];
const labels = {dashboard:"Dashboard",crops:"My Crops",analyze:"Crop Analysis",risk:"Risk Prediction",advice:"Advice & Remedies",stores:"Nearby Stores"};
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
let toastTimer, editingCrop = null, cropRecords = [
 {name:"Tomato", variety:"", location:"", stage:""},
 {name:"Wheat", variety:"", location:"", stage:""}
];
function toast(msg){const t=$("#toast");t.textContent=msg;t.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove("show"),2800)}
function go(page){if(!pages.includes(page))return;pages.forEach(p=>$("#page-"+p).classList.toggle("active",p===page));$$(".nav-item").forEach(b=>b.classList.toggle("active",b.dataset.page===page));$("#crumb").textContent=labels[page];$("#sidebar").classList.remove("open");window.scrollTo({top:0,behavior:"smooth"});}
$$("[data-page]").forEach(b=>b.addEventListener("click",e=>{e.preventDefault();go(b.dataset.page)}));
$$("[data-go]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.go)));
$("#menuBtn").addEventListener("click",()=>$("#sidebar").classList.toggle("open"));
document.addEventListener("click",e=>{if(window.innerWidth<=800 && $("#sidebar").classList.contains("open") && !$("#sidebar").contains(e.target) && !$("#menuBtn").contains(e.target))$("#sidebar").classList.remove("open")});
function openDialog(d){d.showModal()}
function renderCrops(){
 const grid=$("#cropCards");grid.innerHTML="";
 cropRecords.forEach((c,i)=>{
  const isTomato=c.name.toLowerCase().includes("tomato"), emoji=isTomato?"🍅":c.name.toLowerCase().includes("wheat")?"🌾":"🌱";
  const card=document.createElement("article");card.className="crop-large-card";card.dataset.cropName=c.name.toLowerCase();
  card.innerHTML=`<div class="crop-hero ${isTomato?"tomato-hero": "wheat-hero"}"><span>${emoji}</span><div class="crop-badge">DEMO RECORD</div></div><div class="crop-large-body"><div class="crop-title"><div><h3>${escapeHtml(c.name)}</h3><p>${escapeHtml(c.variety||"Crop record")}</p></div><span class="status neutral">Not analyzed</span></div><div class="detail-list"><div><span>Field location</span><strong>${escapeHtml(c.location||"Not added")}</strong></div><div><span>Sowing date</span><strong>Not added</strong></div><div><span>Growth stage</span><strong>${escapeHtml(c.stage||"Not specified")}</strong></div></div><div class="card-actions"><button class="btn btn-outline" data-edit-index="${i}">Edit details</button><button class="btn btn-primary" data-analyze-index="${i}">Analyze crop</button></div></div>`;
  grid.appendChild(card);
 });
 $("#cropCount").innerHTML=`${cropRecords.length} <small>crops</small>`;
 $("#cropListCount").textContent=`${cropRecords.length} crop record${cropRecords.length===1?"":"s"}`;
 $("#cropCards").classList.toggle("hidden",cropRecords.length===0);$("#noCrops").classList.toggle("hidden",cropRecords.length!==0);
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
$("#addCropBtn").addEventListener("click",()=>{editingCrop=null;$("#cropDialogTitle").textContent="Add a crop";$("#cropForm").reset();openDialog($("#cropDialog"))});
$("#cancelCrop").addEventListener("click",()=>$("#cropDialog").close());
$("#cropForm").addEventListener("submit",e=>{e.preventDefault();const name=$("#newCropName").value.trim();if(!name)return;const item={name,variety:$("#newCropVariety").value.trim(),location:$("#newCropLocation").value.trim(),stage:$("#newCropStage").value};if(editingCrop!==null)cropRecords[editingCrop]=item;else cropRecords.push(item);$("#cropDialog").close();renderCrops();toast(`${name} crop record saved`);});
document.addEventListener("click",e=>{const edit=e.target.closest("[data-edit-crop]");const editI=e.target.closest("[data-edit-index]");if(edit||editI){const name=edit?edit.dataset.editCrop:cropRecords[+editI.dataset.editIndex]?.name;editingCrop=edit?cropRecords.findIndex(c=>c.name===name):+editI.dataset.editIndex;if(editingCrop<0)editingCrop=null;const c=editingCrop===null?{name,variety:"",location:"",stage:""}:cropRecords[editingCrop];$("#cropDialogTitle").textContent="Edit crop details";$("#newCropName").value=c.name;$("#newCropVariety").value=c.variety||"";$("#newCropLocation").value=c.location||"";$("#newCropStage").value=c.stage||"";openDialog($("#cropDialog"));return}
 const analyze=e.target.closest("[data-analyze-crop]");const analyzeI=e.target.closest("[data-analyze-index]");if(analyze||analyzeI){const name=analyze?analyze.dataset.analyzeCrop:cropRecords[+analyzeI.dataset.analyzeIndex]?.name;go("analyze");$("#analysisCrop").value=["Tomato","Wheat","Rice","Cotton","Other"].includes(name)?name:"Other";toast(`Ready to analyze a ${name} image`);}
});
$("#cropSearch").addEventListener("input",e=>{const q=e.target.value.toLowerCase();let visible=0;$$(".crop-large-card").forEach(c=>{const yes=c.dataset.cropName.includes(q);c.classList.toggle("hidden",!yes);if(yes)visible++});$("#noCrops").classList.toggle("hidden",visible!==0);});
let selectedFile=null;
const imageInput=$("#imageInput"),zone=$("#uploadZone"),preview=$("#imagePreview"),analyzeBtn=$("#analyzeBtn");
function loadFile(file){if(!file)return;if(!/^image\/(jpeg|png|webp)$/.test(file.type)){toast("Please choose a JPG, PNG or WEBP image.");return;}selectedFile=file;preview.src=URL.createObjectURL(file);preview.classList.remove("hidden");zone.querySelector(".upload-cloud").classList.add("hidden");zone.querySelector("strong").textContent=file.name;zone.querySelector("span").textContent="Image selected · click here to change";analyzeBtn.disabled=false;$("#analysisResult").classList.add("hidden");}
imageInput.addEventListener("change",e=>loadFile(e.target.files[0]));
["dragenter","dragover"].forEach(ev=>zone.addEventListener(ev,e=>{e.preventDefault();zone.classList.add("dragging")}));
["dragleave","drop"].forEach(ev=>zone.addEventListener(ev,e=>{e.preventDefault();zone.classList.remove("dragging")}));
zone.addEventListener("drop",e=>loadFile(e.dataTransfer.files[0]));
analyzeBtn.addEventListener("click",()=>{if(!selectedFile)return;$("#analysisResult").classList.remove("hidden");$("#analysisResult").scrollIntoView({behavior:"smooth",block:"center"});toast("Image selected. No AI model is connected in this demo.");});
$("#resetAnalysis").addEventListener("click",()=>{selectedFile=null;imageInput.value="";preview.src="";preview.classList.add("hidden");zone.querySelector(".upload-cloud").classList.remove("hidden");zone.querySelector("strong").textContent="Drop your image here";zone.querySelector("span").innerHTML='or <b>browse files</b> from your device';analyzeBtn.disabled=true;$("#analysisResult").classList.add("hidden")});
$("#riskBtn").addEventListener("click",()=>{const h=$("#humidity").value,r=$("#rainfall").value;const feedback=$("#riskFeedback");feedback.classList.remove("hidden");if(h===""||r===""||!$("#stageRisk").value||!$("#soil").value){feedback.textContent="Some inputs are missing. Add humidity, rainfall, soil condition and growth stage where known. No risk score has been generated.";toast("Please complete the available risk inputs.");}else{feedback.textContent="Inputs captured for review. A trained prediction model and validated local data are still required to calculate a disease-risk level.";toast("Inputs reviewed. No prediction was generated.");}});
function openInfo(title,copy){$("#infoTitle").textContent=title;$("#infoCopy").textContent=copy;openDialog($("#infoDialog"))}
$("#helpBtn").addEventListener("click",()=>openInfo("Quick guide","Start by adding your crop records. Use Crop Analysis to select a plant photo. Risk Prediction explains which environmental and crop inputs a future model needs. Advice & Remedies provides general safety-first guidance, and Nearby Stores will need a location and a live listings service."));
$("#notificationBtn").addEventListener("click",()=>openInfo("Notifications","There are no live alerts in this prototype. Connect weather and risk services to provide useful, verified notifications."));
$("#safetyBtn").addEventListener("click",()=>openInfo("Treatment safety","Do not apply a pesticide based only on an unverified AI result. Confirm the crop issue, use products registered for the crop and purpose, and follow the full label, protective equipment instructions and pre-harvest interval. Seek advice from a qualified local agricultural expert when uncertain."));
const locationDialog=$("#locationDialog");
["locationBtn","setLocationStore","storeLocationLink","mapLocationBtn"].forEach(id=>$("#"+id).addEventListener("click",()=>openDialog(locationDialog)));
$("#cancelLocation").addEventListener("click",()=>locationDialog.close());
$("#locationForm").addEventListener("submit",e=>{e.preventDefault();const v=$("#locationInput").value.trim();if(!v)return;$("#locationText").textContent=v;locationDialog.close();toast("Location label updated. Live services are not connected.");});
$("#storeSearchBtn").addEventListener("click",()=>toast($("#storeSearch").value.trim()?"Live supplier search is not connected yet.":"Enter a product or store name to search."));
$("#storeSearch").addEventListener("keydown",e=>{if(e.key==="Enter")$("#storeSearchBtn").click()});
renderCrops();