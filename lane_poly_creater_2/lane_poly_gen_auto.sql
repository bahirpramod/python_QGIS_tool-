CREATE OR REPLACE FUNCTION public.lane_poly_generate_auto(
	leftlaneid character varying,
	rightlaneid character varying)
    RETURNS text
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
declare
start_segment geometry;
end_segment geometry;
collect_geom geometry[];
poly_geom geometry;
lgeom geometry;
rgeom geometry;
l_lid character varying;
r_lid character varying;
rec record;
rec1 record;
begin 

select right_lane_id into rec from lane_geom where left_lane_id=leftlaneid;
select left_lane_id into rec1 from lane_geom where right_lane_id=rightlaneid;

if rec.right_lane_id is null then
   raise exception 'Right lane id not found %',rightlaneid;
   --return exception;
end if;

if rec1.left_lane_id is null then
   raise exception 'Left lane id not found %',leftlaneid;
   --return exception;
end if;

l_lid:= leftlaneid;
r_lid:= rightlaneid;

	

  execute 'select geom from lane_lines where lane_id='''||l_lid||'''' into lgeom;	
  execute 'select geom from lane_lines where lane_id='''||r_lid||'''' into rgeom;	
  execute 'select start_seg,end_seg from lane_geom where left_lane_id='''||l_lid||'''' into start_segment,end_segment;
		
                            collect_geom:='{}';
						   collect_geom:=array_append(collect_geom,start_segment);
						   collect_geom:=array_append(collect_geom,lgeom);
						   collect_geom:=array_append(collect_geom,rgeom);
						   collect_geom:=array_append(collect_geom,end_segment);
						   
						    poly_geom:= ST_Multi(ST_Makepolygon(ST_Linemerge(ST_Collect(collect_geom))));
	
	execute 'insert into lane_poly(lane_poly,left_lane_id,right_lane_id,lane_id) values
	('''||poly_geom::text||''','''||leftlaneid||''','''||rightlaneid||''',default)';

return 'Done';
	 
end;
$BODY$;


