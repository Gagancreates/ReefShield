import React from "react";

const OilSpillMap: React.FC = () => {
  return (
    <div className="w-full h-full min-h-[60vh]" style={{height: '100%'}}>
      <iframe
        src="/leaflet.html"
        title="Oil Spill Trajectory Map"
        className="w-full h-full min-h-[60vh] rounded-lg border border-[#0e2533] bg-[#071225]"
        style={{ minHeight: '100vh', height: '100%' }}
      />
    </div>
  );
};

export default OilSpillMap; 