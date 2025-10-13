'use client';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';
import { usePathname, useRouter } from "next/navigation";


interface SymbolTabsProps {
  symbol: string;
}

export default function SymbolTabs({ symbol }: SymbolTabsProps) {
  const pathname = usePathname();
  const router = useRouter();

  // 현재 활성 탭 결정
  const getActiveTab = () => {
    if (pathname === `/market-data/stock/${symbol}`) return "overview";
    if (pathname.includes("/financials")) return "financials";
    if (pathname.includes("/news")) return "news";
    if (pathname.includes("/chart")) return "chart";
    return "overview";
  };

  const activeTab = getActiveTab();

  const handleTabChange = (_event: React.SyntheticEvent, newValue: string) => {
    switch (newValue) {
      case "overview":
        router.push(`/market-data/stock/${symbol}`);
        break;
      case "financials":
        router.push(`/market-data/stock/${symbol}/financials`);
        break;
      case "news":
        router.push(`/market-data/stock/${symbol}/news`);
        break;
      case "chart":
        router.push(`/market-data/stock/${symbol}/chart`);
        break;
    }
  };

  return (
    <Box sx={{ width: '100%'}}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            aria-label="symbol navigation tabs"
            sx={{ pt: 1 , px: 4}}
          >
            <Tab label="Overview" value="overview" />
            <Tab label="Chart" value="chart" />
            <Tab label="Financials" value="financials" />
            <Tab label="News" value="news" />
          </Tabs>
      </Box>
    </Box>
  );
}
