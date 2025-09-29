"use client";

import { Add as AddIcon, Refresh as RefreshIcon } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Fab,
  Skeleton,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import React from "react";

import PageContainer from "@/components/layout/PageContainer";
import CreateWatchlistDialog from "@/components/watchlists/CreateWatchlistDialog";
import WatchlistCard from "@/components/watchlists/WatchlistCard";

import {
  watchlistsCreateWatchlistMutation,
  watchlistsDeleteWatchlistMutation,
  watchlistsListWatchlistsOptions,
  watchlistsUpdateWatchlistMutation,
} from "@/client/@tanstack/react-query.gen";

export default function WatchlistsPage() {
  const queryClient = useQueryClient();
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false);
  const [editDialogOpen, setEditDialogOpen] = React.useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [viewDialogOpen, setViewDialogOpen] = React.useState(false);
  const [selectedWatchlist, setSelectedWatchlist] = React.useState<any>(null);
  const [watchlistToDelete, setWatchlistToDelete] = React.useState<
    string | null
  >(null);

  // 워치리스트 목록 조회
  const {
    data: watchlistsResponse,
    isLoading,
    error,
    refetch,
  } = useQuery(watchlistsListWatchlistsOptions());

  // 백엔드 응답 구조: { watchlists: [...], total_count: number }
  const watchlists = (watchlistsResponse as any)?.watchlists || [];
  const totalCount = (watchlistsResponse as any)?.total_count || 0;

  // 디버깅용 로그
  React.useEffect(() => {
    if (watchlistsResponse) {
      console.log("Watchlists Response:", watchlistsResponse);
      console.log("Parsed watchlists:", watchlists);
      console.log("Total count:", totalCount);
    }
  }, [watchlistsResponse, watchlists, totalCount]);

  // 워치리스트 생성 뮤테이션
  const createMutation = useMutation({
    ...watchlistsCreateWatchlistMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlistsListWatchlists"] });
      setCreateDialogOpen(false);
    },
  });

  // 워치리스트 수정 뮤테이션
  const updateMutation = useMutation({
    ...watchlistsUpdateWatchlistMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlistsListWatchlists"] });
      setEditDialogOpen(false);
      setSelectedWatchlist(null);
    },
  });

  // 워치리스트 삭제 뮤테이션
  const deleteMutation = useMutation({
    ...watchlistsDeleteWatchlistMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlistsListWatchlists"] });
      setDeleteDialogOpen(false);
      setWatchlistToDelete(null);
    },
  });

  const handleCreateWatchlist = (data: any) => {
    createMutation.mutate({
      body: data,
    });
  };

  const handleEditWatchlist = (watchlist: any) => {
    setSelectedWatchlist(watchlist);
    setEditDialogOpen(true);
  };

  const handleUpdateWatchlist = (data: any) => {
    if (selectedWatchlist) {
      updateMutation.mutate({
        body: data,
      });
    }
  };

  const handleDeleteWatchlist = (watchlistName: string) => {
    setWatchlistToDelete(watchlistName);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (watchlistToDelete) {
      deleteMutation.mutate({
        path: { name: watchlistToDelete },
      });
    }
  };

  const handleViewWatchlist = (watchlist: any) => {
    setSelectedWatchlist(watchlist);
    setViewDialogOpen(true);
  };

  if (error) {
    console.error("Watchlists error:", error);
    return (
      <PageContainer
        title="워치리스트"
        breadcrumbs={[{ title: "데이터 관리" }, { title: "워치리스트" }]}
      >
        <Alert severity="error" sx={{ mb: 2 }}>
          워치리스트를 불러오는 중 오류가 발생했습니다:{" "}
          {error.message || String(error)}
        </Alert>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => refetch()}
        >
          다시 시도
        </Button>
      </PageContainer>
    );
  }

  return (
    <>
      <PageContainer
        title="워치리스트"
        breadcrumbs={[{ title: "데이터 관리" }, { title: "워치리스트" }]}
        actions={
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={3}
          >
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => refetch()}
                disabled={isLoading}
              >
                새로고침
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
              >
                새 워치리스트
              </Button>
            </Box>
          </Box>
        }
      >
        {isLoading ? (
          <Box
            display="grid"
            gridTemplateColumns="repeat(auto-fill, minmax(300px, 1fr))"
            gap={3}
          >
            {[...Array(6)].map((_, index) => (
              <Skeleton key={index} variant="rectangular" height={200} />
            ))}
          </Box>
        ) : watchlists && watchlists.length > 0 ? (
          <Box
            display="grid"
            gridTemplateColumns="repeat(auto-fill, minmax(300px, 1fr))"
            gap={3}
          >
            {watchlists.map((watchlist: any, index: number) => (
              <WatchlistCard
                key={watchlist.name || index}
                watchlist={watchlist}
                onEdit={handleEditWatchlist}
                onDelete={handleDeleteWatchlist}
                onView={handleViewWatchlist}
              />
            ))}
          </Box>
        ) : (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            py={8}
            textAlign="center"
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              아직 워치리스트가 없습니다
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              첫 번째 워치리스트를 만들어 관심 종목을 관리해보세요.
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
            >
              첫 워치리스트 만들기
            </Button>
          </Box>
        )}
      </PageContainer>

      {/* 플로팅 액션 버튼 (모바일용) */}
      <Fab
        color="primary"
        aria-label="새 워치리스트 추가"
        sx={{
          position: "fixed",
          bottom: 16,
          right: 16,
          display: { xs: "flex", sm: "none" },
        }}
        onClick={() => setCreateDialogOpen(true)}
      >
        <AddIcon />
      </Fab>

      {/* 생성 다이얼로그 */}
      <CreateWatchlistDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSubmit={handleCreateWatchlist}
        loading={createMutation.isPending}
      />

      {/* 수정 다이얼로그 */}
      <CreateWatchlistDialog
        open={editDialogOpen}
        onClose={() => {
          setEditDialogOpen(false);
          setSelectedWatchlist(null);
        }}
        onSubmit={handleUpdateWatchlist}
        initialData={selectedWatchlist}
        isEdit
        loading={updateMutation.isPending}
      />

      {/* 상세보기 다이얼로그 */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => {
          setViewDialogOpen(false);
          setSelectedWatchlist(null);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          워치리스트 상세 정보: {selectedWatchlist?.name}
        </DialogTitle>
        <DialogContent>
          {selectedWatchlist && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                설명
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                {selectedWatchlist.description || "설명이 없습니다."}
              </Typography>

              <Typography variant="subtitle1" gutterBottom>
                종목 리스트 (
                {selectedWatchlist.symbols?.length ||
                  selectedWatchlist.symbol_count ||
                  0}
                개)
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                {selectedWatchlist.symbols?.length > 0 ? (
                  selectedWatchlist.symbols.map((symbol: string) => (
                    <Chip key={symbol} label={symbol} variant="outlined" />
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    종목 정보를 불러오는 중...
                  </Typography>
                )}
              </Box>

              <Typography variant="subtitle1" gutterBottom>
                설정 정보
              </Typography>
              <Box display="flex" gap={1} mb={2}>
                <Chip
                  label={
                    selectedWatchlist.auto_update
                      ? "자동 업데이트 사용"
                      : "자동 업데이트 비사용"
                  }
                  color={selectedWatchlist.auto_update ? "success" : "default"}
                  variant="outlined"
                />
                {selectedWatchlist.update_interval && (
                  <Chip
                    label={`업데이트 간격: ${selectedWatchlist.update_interval}초`}
                    variant="outlined"
                  />
                )}
              </Box>

              <Typography variant="subtitle1" gutterBottom>
                타임스탬프
              </Typography>
              <Typography variant="body2" color="text.secondary">
                생성일:{" "}
                {new Date(selectedWatchlist.created_at).toLocaleString("ko-KR")}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                마지막 업데이트:{" "}
                {selectedWatchlist.last_updated
                  ? new Date(selectedWatchlist.last_updated).toLocaleString(
                      "ko-KR"
                    )
                  : "없음"}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setViewDialogOpen(false);
              if (selectedWatchlist) {
                handleEditWatchlist(selectedWatchlist);
              }
            }}
            variant="outlined"
          >
            편집
          </Button>
          <Button
            onClick={() => {
              setViewDialogOpen(false);
              setSelectedWatchlist(null);
            }}
          >
            닫기
          </Button>
        </DialogActions>
      </Dialog>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>워치리스트 삭제</DialogTitle>
        <DialogContent>
          <Typography>
            정말로 이 워치리스트를 삭제하시겠습니까? 이 작업은 되돌릴 수
            없습니다.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>취소</Button>
          <Button
            onClick={confirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? "삭제 중..." : "삭제"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
