import os,sys

def parse_dlmerged_trees_and_make_widgets( tfile ):
    """
    We return some dash widgets based on the contents of the tfile passed to this function.
    Here is a list of trees we might want to act on in a standard uboone dlmerged file:

      KEY: TTree	image2d_wire_tree;1	wire tree
  KEY: TTree	chstatus_wire_tree;1	wire tree
  KEY: TTree	image2d_ubspurn_plane0_tree;1	ubspurn_plane0 tree
  KEY: TTree	image2d_ubspurn_plane1_tree;1	ubspurn_plane1 tree
  KEY: TTree	image2d_ubspurn_plane2_tree;1	ubspurn_plane2 tree
  KEY: TTree	image2d_thrumu_tree;1	thrumu tree
  KEY: TTree	image2d_segment_tree;1	segment tree
  KEY: TTree	image2d_instance_tree;1	instance tree
  KEY: TTree	image2d_ancestor_tree;1	ancestor tree
  KEY: TTree	partroi_segment_tree;1	segment tree
  KEY: TTree	image2d_larflow_tree;1	larflow tree
  KEY: TTree	larlite_id_tree;1	LArLite Event ID Tree
  KEY: TTree	gtruth_generator_tree;1	gtruth Tree by generator
  KEY: TTree	mctruth_corsika_tree;1	mctruth Tree by corsika
  KEY: TTree	mctruth_generator_tree;1	mctruth Tree by generator
  KEY: TTree	mcflux_generator_tree;1	mcflux Tree by generator
  KEY: TTree	mcshower_mcreco_tree;1	mcshower Tree by mcreco
  KEY: TTree	daqheadertimeuboone_daq_tree;1	daqheadertimeuboone Tree by daq
  KEY: TTree	hit_gaushit_tree;1	hit Tree by gaushit
  KEY: TTree	hit_portedThresholdhit_tree;1	hit Tree by portedThresholdhit
  KEY: TTree	crthit_crthitcorr_tree;1	crthit Tree by crthitcorr
  KEY: TTree	crttrack_crttrack_tree;1	crttrack Tree by crttrack
  KEY: TTree	ophit_ophitBeam::OverlayStage1OpticalDLrerun_tree;1	ophit Tree by ophitBeam::OverlayStage1OpticalDLrerun
  KEY: TTree	ophit_ophitBeamCalib_tree;1	ophit Tree by ophitBeamCalib
  KEY: TTree	ophit_ophitCosmic::OverlayStage1OpticalDLrerun_tree;1	ophit Tree by ophitCosmic::OverlayStage1OpticalDLrerun
  KEY: TTree	ophit_ophitCosmicCalib_tree;1	ophit Tree by ophitCosmicCalib
  KEY: TTree	opflash_opflashBeam_tree;1	opflash Tree by opflashBeam
  KEY: TTree	opflash_opflashCosmic_tree;1	opflash Tree by opflashCosmic
  KEY: TTree	opflash_simpleFlashBeam_tree;1	opflash Tree by simpleFlashBeam
  KEY: TTree	opflash_simpleFlashBeam::OverlayStage1OpticalDLrerun_tree;1	opflash Tree by simpleFlashBeam::OverlayStage1OpticalDLrerun
  KEY: TTree	opflash_simpleFlashCosmic_tree;1	opflash Tree by simpleFlashCosmic
  KEY: TTree	opflash_simpleFlashCosmic::OverlayStage1OpticalDLrerun_tree;1	opflash Tree by simpleFlashCosmic::OverlayStage1OpticalDLrerun
  KEY: TTree	sps_portedSpacePointsThreshold_tree;1	sps Tree by portedSpacePointsThreshold
  KEY: TTree	trigger_triggersim_tree;1	trigger Tree by triggersim
  KEY: TTree	mctrack_mcreco_tree;1	mctrack Tree by mcreco
  KEY: TTree	ass_inter_ass_tree;1	ass Tree by inter_ass
  KEY: TTree	ass_opflashBeam_tree;1	ass Tree by opflashBeam
  KEY: TTree	ass_opflashCosmic_tree;1	ass Tree by opflashCosmic
  KEY: TTree	ass_portedSpacePointsThreshold_tree;1	ass Tree by portedSpacePointsThreshold
  KEY: TTree	ass_simpleFlashBeam_tree;1	ass Tree by simpleFlashBeam
  KEY: TTree	ass_simpleFlashBeam::OverlayStage1OpticalDLrerun_tree;1	ass Tree by simpleFlashBeam::OverlayStage1OpticalDLrerun
  KEY: TTree	ass_simpleFlashCosmic_tree;1	ass Tree by simpleFlashCosmic
  KEY: TTree	ass_simpleFlashCosmic::OverlayStage1OpticalDLrerun_tree;1	ass Tree by simpleFlashCosmic::OverlayStage1OpticalDLrerun
  KEY: TTree	swtrigger_swtrigger_tree;1	swtrigger Tree by swtrigger
  KEY: TTree	larflowcluster_ssnetshowerreco_tree;1	larflowcluster Tree by ssnetshowerreco
  KEY: TTree	potsummary_generator_tree;1	potsummary Tree by generator
  KEY: TTree	clustermask_mrcnn_masks_tree;1	mrcnn_masks tree
  KEY: TTree	sparseimg_larflow_tree;1	larflow tree
  KEY: TTree	sparseimg_sparseuresnetout_tree;1	sparseuresnetout tree
    """
    pass

def parse_dlmerged_trees_and_make_plots( tfile ):
    """
    We return some dash widgets based on the contents of the tfile passed to this function.
    Here is a list of trees we might want to act on in a standard uboone dlmerged file:

      KEY: TTree	image2d_wire_tree;1	wire tree
  KEY: TTree	chstatus_wire_tree;1	wire tree
  KEY: TTree	image2d_ubspurn_plane0_tree;1	ubspurn_plane0 tree
  KEY: TTree	image2d_ubspurn_plane1_tree;1	ubspurn_plane1 tree
  KEY: TTree	image2d_ubspurn_plane2_tree;1	ubspurn_plane2 tree
  KEY: TTree	image2d_thrumu_tree;1	thrumu tree
  KEY: TTree	image2d_segment_tree;1	segment tree
  KEY: TTree	image2d_instance_tree;1	instance tree
  KEY: TTree	image2d_ancestor_tree;1	ancestor tree
  KEY: TTree	partroi_segment_tree;1	segment tree
  KEY: TTree	image2d_larflow_tree;1	larflow tree
  KEY: TTree	larlite_id_tree;1	LArLite Event ID Tree
  KEY: TTree	gtruth_generator_tree;1	gtruth Tree by generator
  KEY: TTree	mctruth_corsika_tree;1	mctruth Tree by corsika
  KEY: TTree	mctruth_generator_tree;1	mctruth Tree by generator
  KEY: TTree	mcflux_generator_tree;1	mcflux Tree by generator
  KEY: TTree	mcshower_mcreco_tree;1	mcshower Tree by mcreco
  KEY: TTree	daqheadertimeuboone_daq_tree;1	daqheadertimeuboone Tree by daq
  KEY: TTree	hit_gaushit_tree;1	hit Tree by gaushit
  KEY: TTree	hit_portedThresholdhit_tree;1	hit Tree by portedThresholdhit
  KEY: TTree	crthit_crthitcorr_tree;1	crthit Tree by crthitcorr
  KEY: TTree	crttrack_crttrack_tree;1	crttrack Tree by crttrack
  KEY: TTree	ophit_ophitBeam::OverlayStage1OpticalDLrerun_tree;1	ophit Tree by ophitBeam::OverlayStage1OpticalDLrerun
  KEY: TTree	ophit_ophitBeamCalib_tree;1	ophit Tree by ophitBeamCalib
  KEY: TTree	ophit_ophitCosmic::OverlayStage1OpticalDLrerun_tree;1	ophit Tree by ophitCosmic::OverlayStage1OpticalDLrerun
  KEY: TTree	ophit_ophitCosmicCalib_tree;1	ophit Tree by ophitCosmicCalib
  KEY: TTree	opflash_opflashBeam_tree;1	opflash Tree by opflashBeam
  KEY: TTree	opflash_opflashCosmic_tree;1	opflash Tree by opflashCosmic
  KEY: TTree	opflash_simpleFlashBeam_tree;1	opflash Tree by simpleFlashBeam
  KEY: TTree	opflash_simpleFlashBeam::OverlayStage1OpticalDLrerun_tree;1	opflash Tree by simpleFlashBeam::OverlayStage1OpticalDLrerun
  KEY: TTree	opflash_simpleFlashCosmic_tree;1	opflash Tree by simpleFlashCosmic
  KEY: TTree	opflash_simpleFlashCosmic::OverlayStage1OpticalDLrerun_tree;1	opflash Tree by simpleFlashCosmic::OverlayStage1OpticalDLrerun
  KEY: TTree	sps_portedSpacePointsThreshold_tree;1	sps Tree by portedSpacePointsThreshold
  KEY: TTree	trigger_triggersim_tree;1	trigger Tree by triggersim
  KEY: TTree	mctrack_mcreco_tree;1	mctrack Tree by mcreco
  KEY: TTree	ass_inter_ass_tree;1	ass Tree by inter_ass
  KEY: TTree	ass_opflashBeam_tree;1	ass Tree by opflashBeam
  KEY: TTree	ass_opflashCosmic_tree;1	ass Tree by opflashCosmic
  KEY: TTree	ass_portedSpacePointsThreshold_tree;1	ass Tree by portedSpacePointsThreshold
  KEY: TTree	ass_simpleFlashBeam_tree;1	ass Tree by simpleFlashBeam
  KEY: TTree	ass_simpleFlashBeam::OverlayStage1OpticalDLrerun_tree;1	ass Tree by simpleFlashBeam::OverlayStage1OpticalDLrerun
  KEY: TTree	ass_simpleFlashCosmic_tree;1	ass Tree by simpleFlashCosmic
  KEY: TTree	ass_simpleFlashCosmic::OverlayStage1OpticalDLrerun_tree;1	ass Tree by simpleFlashCosmic::OverlayStage1OpticalDLrerun
  KEY: TTree	swtrigger_swtrigger_tree;1	swtrigger Tree by swtrigger
  KEY: TTree	larflowcluster_ssnetshowerreco_tree;1	larflowcluster Tree by ssnetshowerreco
  KEY: TTree	potsummary_generator_tree;1	potsummary Tree by generator
  KEY: TTree	clustermask_mrcnn_masks_tree;1	mrcnn_masks tree
  KEY: TTree	sparseimg_larflow_tree;1	larflow tree
  KEY: TTree	sparseimg_sparseuresnetout_tree;1	sparseuresnetout tree
    """
    pass