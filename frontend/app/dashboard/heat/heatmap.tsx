import React from "react";

const CoralMap: React.FC = () => {
  return (
    <div className="w-full h-full min-h-[60vh]" style={{height: '100%'}}>
      <iframe
        src="/appmap.html"
        title="Heat Wave Simulation"
        className="w-full h-full min-h-[60vh] rounded-lg border border-[#0e2533] bg-[#071225]"
        style={{ minHeight: '70vh', height: '100%' }}
      />
    </div>
  );
};

export default CoralMap; 