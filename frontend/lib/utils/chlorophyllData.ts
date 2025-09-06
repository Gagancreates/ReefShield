// Utility functions for handling chlorophyll data
export interface ChlorophyllData {
  reef: string;
  center_lat: number;
  center_lon: number;
  found: boolean;
  rank: number;
  pixel_lat: number;
  pixel_lon: number;
  chlor_a: number;
  distance_km: number;
}

// Parse CSV data from the public/data/nearest_valid_pixels.csv file
export function parseChlorophyllCSV(csvText: string): ChlorophyllData[] {
  const lines = csvText.trim().split('\n');
  const headers = lines[0].split(',');
  
  return lines.slice(1).map(line => {
    const values = line.split(',');
    return {
      reef: values[0],
      center_lat: parseFloat(values[1]),
      center_lon: parseFloat(values[2]),
      found: values[3] === 'True',
      rank: parseInt(values[4]),
      pixel_lat: parseFloat(values[5]),
      pixel_lon: parseFloat(values[6]),
      chlor_a: parseFloat(values[7]),
      distance_km: parseFloat(values[8])
    };
  });
}

// Get chlorophyll data for a specific location
export function getChlorophyllForLocation(locationName: string, chlorophyllData: ChlorophyllData[]): ChlorophyllData | null {
  // Map location names to reef names in the CSV
  const nameMapping: { [key: string]: string } = {
    'Jolly_Buoy': 'Jolly_Buoy',
    'Neel Islands': 'Neel_Island',
    'Mahatma Gandhi Marine National Park': 'Mahatma_Gandhi_Marine_National_Park',
    'Havelock': 'Havelock'
  };

  const reefName = nameMapping[locationName] || locationName.replace(/\s+/g, '_');
  return chlorophyllData.find(data => data.reef === reefName) || null;
}

// Determine chlorophyll risk level based on threshold
export function getChlorophyllRiskLevel(chlorValue: number, threshold: number = 0.77): 'low' | 'moderate' | 'high' {
  if (chlorValue >= threshold * 1.5) return 'high';
  if (chlorValue >= threshold) return 'moderate';
  return 'low';
}

// Generate chlorophyll chart data for visualization
export function generateChlorophyllChartData(chlorValue: number, threshold: number = 0.77): Array<{
  name: string;
  value: number;
  color: string;
}> {
  const riskLevel = getChlorophyllRiskLevel(chlorValue, threshold);
  
  return [
    {
      name: 'Current Level',
      value: chlorValue,
      color: riskLevel === 'high' ? '#ef4444' : riskLevel === 'moderate' ? '#f59e0b' : '#10b981'
    },
    {
      name: 'Threshold',
      value: threshold,
      color: '#6b7280'
    }
  ];
}

// Load chlorophyll data from the public directory
export async function loadChlorophyllData(): Promise<ChlorophyllData[]> {
  try {
    const response = await fetch('/data/nearest_valid_pixels.csv');
    const csvText = await response.text();
    return parseChlorophyllCSV(csvText);
  } catch (error) {
    console.error('Failed to load chlorophyll data:', error);
    return [];
  }
}