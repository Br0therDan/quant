import { Box, Card, CardContent, Typography } from "@mui/material";

/**
 * LineageGraph 컴포넌트
 * 데이터 계보 시각화
 */
export const LineageGraph = () => {
	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Data Lineage Graph
				</Typography>

				<Box
					sx={{
						height: 400,
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						bgcolor: "grey.100",
						borderRadius: 1,
						mt: 2,
					}}
				>
					<Typography variant="body2" color="text.secondary">
						Interactive lineage graph visualization will be displayed here.
						<br />
						Shows data flow from source → transformation → destination.
					</Typography>
				</Box>

				<Box sx={{ mt: 3, display: "flex", gap: 2, flexWrap: "wrap" }}>
					<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
						<Box
							sx={{
								width: 16,
								height: 16,
								bgcolor: "primary.main",
								borderRadius: "50%",
							}}
						/>
						<Typography variant="caption">Source</Typography>
					</Box>
					<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
						<Box
							sx={{
								width: 16,
								height: 16,
								bgcolor: "success.main",
								borderRadius: "50%",
							}}
						/>
						<Typography variant="caption">Transformation</Typography>
					</Box>
					<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
						<Box
							sx={{
								width: 16,
								height: 16,
								bgcolor: "warning.main",
								borderRadius: "50%",
							}}
						/>
						<Typography variant="caption">Destination</Typography>
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
};
